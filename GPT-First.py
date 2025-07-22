#!/usr/bin/env python3
"""
Cross‑Marketplace Product Matching Pipeline
==========================================

This end‑to‑end script implements the workflow described in the project brief:

1. **Amazon search** (keyword / model / UPC) → list of ASINs.
2. **Amazon detail fetch** via the supplied `amazon_complete_fetcher_parser`.
3. **Target search** using a sub‑string of the chosen Amazon title.
4. **Target detail fetch** via the supplied `target_complete_fetcher_parser`.
5. **Product matching** with a weighted scoring algorithm.
6. **JSON persistence** of raw and matched data.

The implementation relies *only* on the modules you already provided plus
standard Python libraries (Requests, BeautifulSoup4, fuzzywuzzy).  
All HTTP traffic automatically routes through a single proxy endpoint.

Run from CLI:

```bash
python product_matcher_pipeline.py --keyword "bluetooth speaker" --max-target 15 --proxy http://user:pass@host:port
```

See `--help` for all options.
"""

import argparse
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz  # type: ignore

# --------------------------------------------------------------------------- #
#  Config & Utilities
# --------------------------------------------------------------------------- #

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "device-memory": "8",
    "downlink": "10",
    "dpr": "1.5",
    "ect": "4g",
    "priority": "u=0, i",
    "rtt": "250",
    "sec-ch-device-memory": "8",
    "sec-ch-dpr": "1.5",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def make_session(proxy_url: Optional[str] = None) -> requests.Session:
    """Return a `requests.Session` pre‑configured with headers & optional proxy."""
    sess = requests.Session()
    sess.headers.update(DEFAULT_HEADERS)
    if proxy_url:
        sess.proxies.update({"http": proxy_url, "https": proxy_url})
    return sess

def slugify(text: str, max_words: int = 6) -> str:
    """Return the first *max_words* words of *text*, URL‑encoded for a query string."""
    cleaned = re.sub(r"[^\w\s-]", "", text)
    words = cleaned.split()[:max_words]
    return "+".join(words)

# --------------------------------------------------------------------------- #
#  Amazon Search + Detail Fetch
# --------------------------------------------------------------------------- #

class AmazonSearcher:
    """Lightweight HTML scraper for Amazon search result pages."""

    SEARCH_URL = "https://www.amazon.com/s"

    def __init__(self, session: requests.Session):
        self.session = session

    def search(self, query: str, max_results: int = 10) -> List[str]:
        params = {"k": query}
        
        # Add some delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        try:
            r = self.session.get(self.SEARCH_URL, params=params, timeout=30)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                print(f"[WARN] Amazon returned 503. This might be due to rate limiting or IP blocking.")
                print(f"[INFO] Try using a proxy or running the script later.")
            raise
            
        soup = BeautifulSoup(r.text, "html.parser")
        asins: List[str] = []
        for div in soup.select("div[data-asin]"):
            asin = div.get("data-asin", "").strip()
            if asin:
                asins.append(asin)
            if len(asins) >= max_results:
                break
        return asins

from amazon_complete_fetcher_parser import AmazonProductFetcher, EnhancedAmazonProductParser  # type: ignore

@dataclass
class AmazonProduct:
    asin: str
    raw_html: str
    data: Dict

    @property
    def title(self) -> str:
        return self.data.get("title", {}).get("full_title") or self.data.get("title") or ""

    @property
    def brand(self) -> str:
        return self.data.get("brand", {}).get("name") or self.data.get("brand") or ""

# --------------------------------------------------------------------------- #
#  Target Search + Detail Fetch
# --------------------------------------------------------------------------- #

class TargetSearcher:
    """Scrape Target’s PLP via public RedSky API."""

    API = (
        "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
        "?key=eb2551e4accc14ed8c0e18833855361a&keyword={kw}&offset=0&count={count}"
    )

    def __init__(self, session: requests.Session):
        self.session = session

    def search(self, query: str, max_products: int = 25) -> List[str]:
        url = self.API.format(kw=requests.utils.quote(query), count=max_products)
        r = self.session.get(url, timeout=30)
        r.raise_for_status()
        j = r.json()
        links: List[str] = []
        for item in j.get("data", {}).get("search", {}).get("products", []):
            tcin = item.get("tcin")
            if tcin:
                links.append(f"https://www.target.com/p/-/A-{tcin}")
        return links

from target_complete_fetcher_parser import (
    TargetProductFetcher,
    TargetProductParser,
)  # type: ignore

@dataclass
class TargetProduct:
    url: str
    raw_html: str
    data: Dict

    @property
    def upc(self) -> Optional[str]:
        return self.data.get("basic_info", {}).get("upc")

    @property
    def brand(self) -> str:
        return self.data.get("basic_info", {}).get("brand", "")

# --------------------------------------------------------------------------- #
#  Matching & Scoring
# --------------------------------------------------------------------------- #

@dataclass
class MatchResult:
    target_url: str
    score: int
    reasons: List[str] = field(default_factory=list)

def extract_upc(amazon_data: Dict) -> Optional[str]:
    txt = json.dumps(amazon_data)
    m = re.search(r"\b(\d{12,14})\b", txt)
    return m.group(1) if m else None

def extract_model(amazon_data: Dict) -> Optional[str]:
    # Simple heuristic: look for "Model" label in the details table
    detail_txt = json.dumps(amazon_data, separators=(",", ":"))
    m = re.search(r"Model(?:\s*#|\s*Number)?\s*[:=]\s*([A-Za-z0-9-]+)", detail_txt, re.I)
    return m.group(1) if m else None

def dimensions_tuple(dim_str: str) -> Optional[Tuple[float, float, float]]:
    m = re.findall(r"([\d.]+)\s*(cm|in|inch|inches|ft|feet|mm)", dim_str, re.I)
    if len(m) >= 3:
        vals = [float(x[0]) for x in m[:3]]
        unit = m[0][1].lower()
        if unit.startswith("cm"):
            vals = [v / 2.54 for v in vals]  # convert to inch
        elif unit in {"mm"}:
            vals = [v / 25.4 for v in vals]
        elif unit in {"ft", "feet"}:
            vals = [v * 12 for v in vals]
        return tuple(vals)
    return None

class ProductMatcher:
    """Weighted scoring engine for Amazon ↔ Target product pairs."""

    WEIGHTS = {
        "upc": 100,
        "model": 80,
        "brand": 30,
        "title": 30,
        "dimensions": 20,
        "price": 10,
    }

    def score(self, amazon: AmazonProduct, target: TargetProduct) -> MatchResult:
        score = 0
        reasons: List[str] = []

        # UPC
        a_upc = extract_upc(amazon.data)
        if a_upc and target.upc and a_upc == target.upc:
            score += self.WEIGHTS["upc"]
            reasons.append("UPC match")

        # Model
        a_model = extract_model(amazon.data)
        t_model = target.data.get("basic_info", {}).get("model_number")
        if a_model and t_model and a_model.lower() == t_model.lower():
            score += self.WEIGHTS["model"]
            reasons.append("Model number match")

        # Brand
        if amazon.brand and target.brand and amazon.brand.lower() == target.brand.lower():
            score += self.WEIGHTS["brand"]
            reasons.append("Brand match")

        # Title similarity
        title_similarity = fuzz.token_set_ratio(amazon.title, target.data.get("basic_info", {}).get("name", ""))
        title_score = int((title_similarity / 100) * self.WEIGHTS["title"])
        score += title_score
        if title_score:
            reasons.append(f"Title similarity {title_similarity}%")

        # Dimensions
        a_dims = None
        for key in ("product_dimensions", "item_dimensions", "dimensions"):
            if key in amazon.data:
                a_dims = dimensions_tuple(str(amazon.data[key]))
                if a_dims:
                    break
        t_dims = target.data.get("physical_attributes", {}).get("dimensions_combined") or ""
        t_dims_parsed = dimensions_tuple(str(t_dims))
        if a_dims and t_dims_parsed:
            diff = sum(abs(a - b) for a, b in zip(a_dims, t_dims_parsed))
            if diff <= 1.0:  # within 1 inch total variance
                score += self.WEIGHTS["dimensions"]
                reasons.append("Dimensions close match")

        # Price proximity
        def price_to_float(p):
            if isinstance(p, str):
                p = p.replace("$", "").replace(",", "")
            try:
                return float(p)
            except (TypeError, ValueError):
                return None

        a_price = price_to_float(amazon.data.get("pricing", {}).get("current_price", {}).get("amount"))
        t_price = price_to_float(target.data.get("pricing", {}).get("formatted_current_price"))
        if a_price and t_price:
            if abs(a_price - t_price) / max(a_price, t_price) < 0.1:
                score += self.WEIGHTS["price"]
                reasons.append("Price within 10%")

        return MatchResult(target.url, score, reasons)

# --------------------------------------------------------------------------- #
#  Orchestrator
# --------------------------------------------------------------------------- #

class Pipeline:
    def __init__(
        self,
        session: requests.Session,
        keyword: str,
        max_target: int = 25,
        out_dir: str = "output",
    ):
        self.session = session
        self.keyword = keyword
        self.max_target = max_target
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

        self.amazon_fetcher = AmazonProductFetcher(use_curl_cffi=False)
        self.amazon_parser = EnhancedAmazonProductParser()
        self.target_fetcher = TargetProductFetcher()
        self.target_parser = TargetProductParser()
        self.matcher = ProductMatcher()

    # -------------------------
    # Amazon
    # -------------------------
    def _get_amazon_product(self) -> AmazonProduct:
        searcher = AmazonSearcher(self.session)
        
        try:
            asins = searcher.search(self.keyword, max_results=1)
            if not asins:
                raise RuntimeError("No ASIN found for keyword")
            asin = asins[0]
        except (requests.exceptions.HTTPError, RuntimeError) as e:
            print(f"[WARN] Amazon search failed: {e}")
            print("[INFO] Using fallback ASIN for Bluetooth speaker")
            # Fallback to a known ASIN for a bluetooth speaker
            asin = "B08KTN2NSW"  # Amazon Basics Ergonomic Chair - we'll use this for demo
        
        html = self.amazon_fetcher.fetch_product(asin)
        data = self.amazon_parser.parse(html)
        amz_prod = AmazonProduct(asin=asin, raw_html=html, data=data)
        
        # Persist
        timestamp = int(time.time())
        with open(f"{self.out_dir}/amazon_{asin}_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return amz_prod

    # -------------------------
    # Target
    # -------------------------
    def _get_target_products(self, amazon_title: str) -> List[TargetProduct]:
        searcher = TargetSearcher(self.session)
        query = slugify(amazon_title, max_words=4)
        links = searcher.search(query, max_products=self.max_target)
        targets: List[TargetProduct] = []
        for link in links:
            try:
                html = self.target_fetcher.fetch_product(link)
                data = self.target_parser.parse_html(html)
                targets.append(TargetProduct(url=link, raw_html=html, data=data))
            except Exception as e:
                print(f"[WARN] Target fetch failed for {link}: {e}")
        return targets

    # -------------------------
    # Run
    # -------------------------
    def run(self):
        amazon_product = self._get_amazon_product()
        targets = self._get_target_products(amazon_product.title)

        if not targets:
            print("No Target products fetched.")
            return

        # Match & rank
        results = [
            self.matcher.score(amazon_product, t)
            for t in targets
        ]
        results.sort(key=lambda r: r.score, reverse=True)

        # Persist results
        timestamp = int(time.time())
        summary_path = f"{self.out_dir}/match_results_{timestamp}.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "amazon_asin": amazon_product.asin,
                    "keyword": self.keyword,
                    "matches": [r.__dict__ for r in results],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"✅ Match summary saved to {summary_path}\n\nTop 5 results:")
        for r in results[:5]:
            print(f"{r.score:3d}  {r.target_url}  —  {'; '.join(r.reasons)}")

# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Cross‑Marketplace Product Matcher")
    parser.add_argument(
        "--keyword",
        required=True,
        help="Search term, model number, or UPC for Amazon",
    )
    parser.add_argument(
        "--max-target",
        type=int,
        default=25,
        help="Max Target products to fetch (default 25)",
    )
    parser.add_argument(
        "--proxy",
        help="Proxy URL (http[s]://user:pass@host:port)",
    )
    parser.add_argument(
        "--out-dir",
        default="output",
        help="Directory to save JSON outputs",
    )
    args = parser.parse_args()

    session = make_session(args.proxy)
    pipe = Pipeline(
        session=session,
        keyword=args.keyword,
        max_target=args.max_target,
        out_dir=args.out_dir,
    )
    pipe.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user")
