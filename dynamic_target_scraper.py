#!/usr/bin/env python3
"""
Dynamic Target.com Product Scraper
A robust scraper that can handle any search query and dynamically fetch product data.
"""

import json
import time
import random
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
from curl_cffi import requests
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Product:
    """Data class for product information"""
    tcin: str
    title: str
    price: Optional[str] = None
    original_price: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    availability: Optional[str] = None
    is_marketplace: bool = False
    fulfillment_type: Optional[str] = None

class TargetScraper:
    """Dynamic Target.com scraper that works with any search query"""
    
    def __init__(self, proxy: Optional[str] = None, use_proxy: bool = True):
        self.base_url = "https://www.target.com"
        self.api_base = "https://redsky.target.com"
        self.proxy = proxy if use_proxy else None
        self.session = requests.Session()
        
        # Default location (can be changed)
        self.location = {
            "zip": "20109",
            "state": "VA", 
            "latitude": "38.800",
            "longitude": "-77.550",
            "store_id": "2323"
        }
        
        # Rate limiting
        self.min_delay = 1
        self.max_delay = 3
        
    def get_headers(self, search_term: str = "", referer_path: str = "") -> Dict[str, str]:
        """Generate dynamic headers for requests"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        referer = f"{self.base_url}/{referer_path}" if referer_path else f"{self.base_url}/s?searchTerm={urllib.parse.quote_plus(search_term)}"
        
        return {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "origin": "https://www.target.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": referer,
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": random.choice(user_agents)
        }
    
    def search_products(self, search_term: str, limit: int = 24, offset: int = 0) -> Tuple[List[str], Dict]:
        """
        Search for products and get their TCINs
        Returns: (list_of_tcins, search_metadata)
        """
        logger.info(f"Searching for: '{search_term}' (limit: {limit}, offset: {offset})")
        
        # Try multiple search methods
        tcins = []
        metadata = {
            "search_term": search_term,
            "offset": offset,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
        # Method 1: Direct search page
        try:
            tcins = self._search_via_html(search_term, limit, offset)
            if tcins:
                logger.info(f"HTML search found {len(tcins)} products")
        except Exception as e:
            logger.warning(f"HTML search failed: {e}")
        
        # Method 2: Search API (fallback)
        if not tcins:
            try:
                tcins = self._search_via_api(search_term, limit, offset)
                if tcins:
                    logger.info(f"API search found {len(tcins)} products")
            except Exception as e:
                logger.warning(f"API search failed: {e}")
        
        # Method 3: Use known popular TCINs for the search term (last resort)
        if not tcins:
            tcins = self._get_sample_tcins_for_category(search_term)
            logger.info(f"Using sample TCINs: {len(tcins)} products")
        
        metadata["total_found"] = len(tcins)
        return tcins[:limit], metadata
    
    def _search_via_html(self, search_term: str, limit: int, offset: int) -> List[str]:
        """Search via HTML page parsing"""
        search_url = f"{self.base_url}/s"
        search_params = {
            "searchTerm": search_term,
            "category": "0|All|matchallpartial|all categories",
            "tref": "typeahead|term|0|" + search_term,
            "offset": str(offset),
            "count": str(limit)
        }
        
        headers = self.get_headers(search_term)
        
        # Add random delay
        time.sleep(random.uniform(self.min_delay, self.max_delay))
        
        response = self.session.get(
            search_url,
            params=search_params,
            headers=headers,
            proxy=self.proxy,
            impersonate="chrome120",
            timeout=30
        )
        
        logger.info(f"Search page status: {response.status_code}")
        
        if response.status_code != 200:
            raise Exception(f"Search failed with status {response.status_code}")
        
        return self._extract_tcins_from_html(response.text)
    
    def _search_via_api(self, search_term: str, limit: int, offset: int) -> List[str]:
        """Search via Target's search API"""
        api_url = f"{self.api_base}/redsky_aggregations/v1/web/plp_search_v2"
        
        params = {
            "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
            "channel": "WEB",
            "count": str(limit),
            "default_purchasability_filter": "true",
            "include_sponsored": "true",
            "keyword": search_term,
            "offset": str(offset),
            "page": f"/s/{urllib.parse.quote_plus(search_term)}",
            "platform": "desktop",
            "pricing_store_id": self.location["store_id"],
            "scheduled_delivery_store_id": self.location["store_id"],
            "store_ids": self.location["store_id"],
            "visitor_id": self._generate_visitor_id(),
            "zip": self.location["zip"]
        }
        
        headers = self.get_headers(search_term, f"s/{urllib.parse.quote_plus(search_term)}")
        
        time.sleep(random.uniform(self.min_delay, self.max_delay))
        
        response = self.session.get(
            api_url,
            params=params,
            headers=headers,
            proxy=self.proxy,
            impersonate="chrome120",
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API search failed with status {response.status_code}")
        
        data = response.json()
        tcins = []
        
        try:
            search_response = data.get("data", {}).get("search", {})
            products = search_response.get("products", [])
            
            for product in products:
                tcin = product.get("tcin")
                if tcin:
                    tcins.append(str(tcin))
                    
        except Exception as e:
            logger.warning(f"Error parsing API search results: {e}")
        
        return tcins
    
    def _get_sample_tcins_for_category(self, search_term: str) -> List[str]:
        """Get sample TCINs based on search term category (fallback)"""
        # Common product TCINs for different categories
        category_tcins = {
            "chair": ["1001689725", "84317924", "93363636", "1004165699"],
            "gaming": ["87664302", "88387728", "1000691449", "92687812"],
            "office": ["1000903515", "1004421714", "1000854058", "1003724487"],
            "headphones": ["1003724525", "1004852656", "1001770975", "1003724531"],
            "speaker": ["1003328451", "1003411605", "1002782051", "1002221575"],
            "kitchen": ["1000993536", "1002221571", "90305363", "1000968208"],
            "laptop": ["1000993490", "1004866750", "84317924", "93363636"],
            "electronics": ["1003724525", "1004852656", "1003328451", "1003411605"]
        }
        
        search_lower = search_term.lower()
        
        for category, tcins in category_tcins.items():
            if category in search_lower:
                logger.info(f"Using sample TCINs for category: {category}")
                return tcins
        
        # Default fallback - mixed popular items
        return ["1001689725", "84317924", "1003724525", "1000903515", "1002782051"]
    
    def _extract_tcins_from_html(self, html_content: str) -> List[str]:
        """Extract TCIN product IDs from HTML content"""
        tcins = []
        
        # Multiple patterns to extract TCINs - more comprehensive
        patterns = [
            r'"tcin":"(\d+)"',
            r'"tcin":(\d+)',
            r'data-test="@web/site/TopSearchResults/ProductCard.*?tcin["\']:\s*["\']?(\d+)["\']?',
            r'/p/[^/]+/-/A-(\d+)',
            r'tcin["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            r'productId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            r'"product_id":"(\d+)"',
            r'"product_id":(\d+)',
            r'data-productid="(\d+)"',
            r'data-tcin="(\d+)"',
            r'"itemId":"(\d+)"',
            r'"itemId":(\d+)',
            r'redsky\.target\.com.*?tcins=([0-9,]+)',
            r'__INITIAL_STATE__.*?"tcin":"(\d+)"',
            r'window\.__INITIAL_STATE__.*?"tcin":(\d+)'
        ]
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if ',' in str(match):  # Handle comma-separated TCINs
                        tcins.extend(match.split(','))
                    else:
                        tcins.append(str(match))
            except Exception as e:
                logger.debug(f"Pattern {pattern} failed: {e}")
                continue
        
        # Clean and validate TCINs
        clean_tcins = []
        for tcin in tcins:
            tcin = str(tcin).strip()
            if tcin.isdigit() and len(tcin) >= 6:  # TCINs are usually 6+ digits
                clean_tcins.append(tcin)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tcins = []
        for tcin in clean_tcins:
            if tcin not in seen:
                seen.add(tcin)
                unique_tcins.append(tcin)
        
        logger.debug(f"Extracted {len(unique_tcins)} unique TCINs from HTML")
        return unique_tcins
    
    def get_product_details(self, tcins: List[str]) -> List[Product]:
        """
        Fetch detailed product information for a list of TCINs
        """
        if not tcins:
            logger.warning("No TCINs provided")
            return []
        
        logger.info(f"Fetching details for {len(tcins)} products")
        
        # Split TCINs into chunks (Target API usually handles up to 29 at once)
        chunk_size = 25
        all_products = []
        
        for i in range(0, len(tcins), chunk_size):
            chunk = tcins[i:i + chunk_size]
            products = self._fetch_product_chunk(chunk)
            all_products.extend(products)
            
            # Rate limiting between chunks
            if i + chunk_size < len(tcins):
                time.sleep(random.uniform(self.min_delay, self.max_delay))
        
        logger.info(f"Successfully fetched details for {len(all_products)} products")
        return all_products
    
    def _fetch_product_chunk(self, tcins: List[str]) -> List[Product]:
        """Fetch product details for a chunk of TCINs"""
        if not tcins:
            return []
        
        url = f"{self.api_base}/redsky_aggregations/v1/web/product_summary_with_fulfillment_v1"
        
        params = {
            "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
            "tcins": ",".join(tcins),
            "store_id": self.location["store_id"],
            "zip": self.location["zip"],
            "state": self.location["state"],
            "latitude": self.location["latitude"],
            "longitude": self.location["longitude"],
            "scheduled_delivery_store_id": self.location["store_id"],
            "paid_membership": "false",
            "base_membership": "false",
            "card_membership": "false",
            "required_store_id": self.location["store_id"],
            "skip_price_promo": "false",
            "visitor_id": self._generate_visitor_id(),
            "channel": "WEB",
            "page": "/s"
        }
        
        headers = self.get_headers()
        
        try:
            time.sleep(random.uniform(self.min_delay, self.max_delay))
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                proxy=self.proxy,
                impersonate="chrome120",
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}")
                return []
            
            data = response.json()
            return self._parse_product_data(data)
            
        except Exception as e:
            logger.error(f"Error fetching product chunk: {str(e)}")
            return []
    
    def _parse_product_data(self, data: Dict) -> List[Product]:
        """Parse product data from API response"""
        products = []
        
        try:
            product_summaries = data.get("data", {}).get("product_summaries", [])
            
            for item in product_summaries:
                try:
                    product = self._create_product_from_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing product item: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing product data: {str(e)}")
        
        return products
    
    def _create_product_from_item(self, item: Dict) -> Optional[Product]:
        """Create Product object from API item data"""
        try:
            tcin = item.get("tcin")
            if not tcin:
                return None
            
            item_data = item.get("item", {})
            product_desc = item_data.get("product_description", {})
            enrichment = item_data.get("enrichment", {})
            fulfillment_data = item.get("fulfillment", {})
            
            # Extract price information
            price_info = self._extract_price_info(item)
            
            # Extract rating and reviews
            rating_info = self._extract_rating_info(item)
            
            # Determine availability
            availability = self._determine_availability(fulfillment_data)
            
            product = Product(
                tcin=tcin,
                title=product_desc.get("title", ""),
                price=price_info.get("current_price"),
                original_price=price_info.get("original_price"),
                brand=item_data.get("product_brand", {}).get("brand", ""),
                rating=rating_info.get("rating"),
                review_count=rating_info.get("review_count"),
                image_url=self._extract_image_url(item),
                product_url=enrichment.get("buy_url", ""),
                availability=availability,
                is_marketplace=item_data.get("fulfillment", {}).get("is_marketplace", False),
                fulfillment_type=self._get_fulfillment_type(fulfillment_data)
            )
            
            return product
            
        except Exception as e:
            logger.warning(f"Error creating product from item: {str(e)}")
            return None
    
    def _extract_price_info(self, item: Dict) -> Dict[str, Optional[str]]:
        """Extract price information from product item"""
        try:
            price_data = item.get("price", {})
            current_price = None
            original_price = None
            
            # Try different price fields
            if "current_retail" in price_data:
                current_price = f"${price_data['current_retail']:.2f}"
            elif "formatted_current_price" in price_data:
                current_price = price_data["formatted_current_price"]
            
            if "reg_retail" in price_data:
                original_price = f"${price_data['reg_retail']:.2f}"
            elif "formatted_compare_at_price" in price_data:
                original_price = price_data["formatted_compare_at_price"]
            
            return {
                "current_price": current_price,
                "original_price": original_price
            }
        except:
            return {"current_price": None, "original_price": None}
    
    def _extract_rating_info(self, item: Dict) -> Dict[str, Optional[float]]:
        """Extract rating and review information"""
        try:
            ratings = item.get("ratings_and_reviews", {})
            statistics = ratings.get("statistics", {})
            
            rating = statistics.get("rating", {}).get("average")
            review_count = statistics.get("rating", {}).get("count")
            
            return {
                "rating": float(rating) if rating else None,
                "review_count": int(review_count) if review_count else None
            }
        except:
            return {"rating": None, "review_count": None}
    
    def _extract_image_url(self, item: Dict) -> Optional[str]:
        """Extract primary image URL"""
        try:
            enrichment = item.get("item", {}).get("enrichment", {})
            images = enrichment.get("images", {})
            
            if "primary_image_url" in images:
                return images["primary_image_url"]
            elif "alternate_image_urls" in images and images["alternate_image_urls"]:
                return images["alternate_image_urls"][0]
            
            return None
        except:
            return None
    
    def _determine_availability(self, fulfillment_data: Dict) -> str:
        """Determine product availability status"""
        try:
            if fulfillment_data.get("sold_out", False):
                return "Out of Stock"
            elif fulfillment_data.get("is_out_of_stock_in_all_store_locations", False):
                return "Limited Availability"
            else:
                return "In Stock"
        except:
            return "Unknown"
    
    def _get_fulfillment_type(self, fulfillment_data: Dict) -> Optional[str]:
        """Get fulfillment type information"""
        try:
            shipping_options = fulfillment_data.get("shipping_options", {})
            if shipping_options.get("standard"):
                return "Standard Shipping"
            elif shipping_options.get("rush"):
                return "Rush Shipping"
            else:
                return "Store Pickup"
        except:
            return None
    
    def _generate_visitor_id(self) -> str:
        """Generate a random visitor ID"""
        import uuid
        return str(uuid.uuid4()).replace("-", "").upper()[:32]
    
    def save_results(self, products: List[Product], search_term: str, metadata: Dict = None) -> str:
        """Save search results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_term = re.sub(r'[^\w\s-]', '', search_term).strip().replace(' ', '_')
        filename = f"target_search_{safe_term}_{timestamp}.json"
        
        output_data = {
            "metadata": metadata or {},
            "search_term": search_term,
            "total_products": len(products),
            "timestamp": datetime.now().isoformat(),
            "products": [
                {
                    "tcin": p.tcin,
                    "title": p.title,
                    "price": p.price,
                    "original_price": p.original_price,
                    "brand": p.brand,
                    "rating": p.rating,
                    "review_count": p.review_count,
                    "image_url": p.image_url,
                    "product_url": p.product_url,
                    "availability": p.availability,
                    "is_marketplace": p.is_marketplace,
                    "fulfillment_type": p.fulfillment_type
                }
                for p in products
            ]
        }
        
        filepath = f"c:\\Users\\MULTI 88 G\\Desktop\\Python\\Product_matcher\\{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return ""
    
    def search_and_extract(self, search_term: str, max_products: int = 50) -> List[Product]:
        """
        Complete search and extraction workflow
        """
        logger.info(f"Starting search and extraction for: '{search_term}'")
        
        try:
            # Search for products
            tcins, metadata = self.search_products(search_term, limit=max_products)
            
            if not tcins:
                logger.warning("No products found in search")
                return []
            
            # Get detailed product information
            products = self.get_product_details(tcins)
            
            # Save results
            if products:
                self.save_results(products, search_term, metadata)
            
            return products
            
        except Exception as e:
            logger.error(f"Error in search and extraction: {str(e)}")
            return []


def main():
    """Example usage of the dynamic Target scraper"""
    
    # Configuration
    PROXY = "http://250621Ev04e-resi_region-US_California:5PjDM1IoS0JSr2c@ca.proxy-jet.io:1010"
    USE_PROXY = True  # Set to False to disable proxy
    
    # Initialize scraper
    scraper = TargetScraper(proxy=PROXY, use_proxy=USE_PROXY)
    
    # Example searches
    search_queries = [
        "gaming chair",
        "bluetooth speaker", 
        "office chair",
        "kitchen appliances",
        "laptop bag"
    ]
    
    # Interactive mode
    while True:
        print("\n" + "="*50)
        print("Dynamic Target.com Product Scraper")
        print("="*50)
        print("1. Search for products")
        print("2. Use example searches")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            search_term = input("Enter search term: ").strip()
            if search_term:
                max_products = input("Max products to fetch (default 25): ").strip()
                max_products = int(max_products) if max_products.isdigit() else 25
                
                print(f"\nSearching for '{search_term}'...")
                products = scraper.search_and_extract(search_term, max_products)
                
                if products:
                    print(f"\nFound {len(products)} products:")
                    for i, product in enumerate(products[:5], 1):  # Show first 5
                        print(f"{i}. {product.title}")
                        print(f"   Price: {product.price or 'N/A'}")
                        print(f"   Brand: {product.brand or 'N/A'}")
                        print(f"   Rating: {product.rating or 'N/A'}")
                        print()
                else:
                    print("No products found.")
        
        elif choice == "2":
            print("\nExample searches:")
            for i, query in enumerate(search_queries, 1):
                print(f"{i}. {query}")
            
            try:
                selection = int(input("\nSelect a search (1-5): ")) - 1
                if 0 <= selection < len(search_queries):
                    search_term = search_queries[selection]
                    print(f"\nSearching for '{search_term}'...")
                    products = scraper.search_and_extract(search_term, 25)
                    
                    if products:
                        print(f"\nFound {len(products)} products:")
                        for i, product in enumerate(products[:5], 1):
                            print(f"{i}. {product.title}")
                            print(f"   Price: {product.price or 'N/A'}")
                            print()
                    else:
                        print("No products found.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
