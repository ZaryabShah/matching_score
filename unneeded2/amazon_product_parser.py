"""
Amazon Product Parser
A comprehensive parser to extract detailed product information from Amazon product pages
for cross-platform product matching.
"""

import re
import json
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse


class AmazonProductParser:
    def __init__(self):
        self.base_url = "https://www.amazon.com"
        
    def parse(self, html_content: str, source_url: str = None) -> Dict[str, Any]:
        """
        Main parsing function that extracts all product information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract ASIN from URL or page
        asin = self._extract_asin(soup, source_url)
        
        product_data = {
            # Basic identifiers
            "asin": asin,
            "source_url": source_url,
            "parsed_at": datetime.now().isoformat(),
            
            # Product title and brand
            "title": self._extract_title(soup),
            "brand": self._extract_brand(soup),
            
            # Product images
            "images": self._extract_images(soup),
            
            # Pricing information
            "pricing": self._extract_pricing(soup),
            
            # Product details and specifications
            "specifications": self._extract_specifications(soup),
            "product_details": self._extract_product_details(soup),
            "feature_bullets": self._extract_feature_bullets(soup),
            
            # Category and classification
            "categories": self._extract_categories(soup),
            "breadcrumbs": self._extract_breadcrumbs(soup),
            
            # Reviews and ratings
            "reviews": self._extract_review_summary(soup),
            
            # Availability and shipping
            "availability": self._extract_availability(soup),
            "shipping": self._extract_shipping_info(soup),
            
            # Variations and options
            "variations": self._extract_variations(soup),
            
            # Additional product info
            "description": self._extract_description(soup),
            "videos": self._extract_videos(soup),
            "warranty": self._extract_warranty_info(soup),
            
            # SEO and metadata
            "meta_data": self._extract_meta_data(soup),
            
            # Related products
            "related_products": self._extract_related_products(soup)
        }
        
        return product_data
    
    def _extract_asin(self, soup: BeautifulSoup, source_url: str = None) -> Optional[str]:
        """Extract ASIN from URL or page content"""
        # Try URL first
        if source_url:
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', source_url)
            if asin_match:
                return asin_match.group(1)
        
        # Try page content
        asin_patterns = [
            r'"asin":\s*"([A-Z0-9]{10})"',
            r'data-asin="([A-Z0-9]{10})"',
            r'asin:\s*"([A-Z0-9]{10})"'
        ]
        
        for pattern in asin_patterns:
            match = re.search(pattern, str(soup))
            if match:
                return match.group(1)
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        selectors = [
            "#productTitle",
            ".product-title",
            "#title span",
            "h1 span[id*='title']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand information"""
        # Try byline info
        byline = soup.select_one("#bylineInfo")
        if byline:
            brand_text = byline.get_text().strip()
            if "Visit the" in brand_text and "Store" in brand_text:
                return brand_text.replace("Visit the", "").replace("Store", "").strip()
        
        # Try other selectors
        selectors = [
            "[data-brand]",
            ".a-brand",
            "#brand",
            "a[href*='/stores/']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.has_attr('data-brand'):
                    return element['data-brand']
                return element.get_text().strip()
        
        return None
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract product images"""
        images = []
        
        # Main product images
        img_selectors = [
            "#landingImage",
            "#ebooksImgBlkFront",
            "[data-action='main-image-click'] img",
            ".a-dynamic-image"
        ]
        
        for selector in img_selectors:
            for img in soup.select(selector):
                if img.get('src') or img.get('data-src'):
                    image_url = img.get('src') or img.get('data-src')
                    if image_url and not image_url.startswith('data:'):
                        images.append({
                            "url": urljoin(self.base_url, image_url),
                            "alt": img.get('alt', ''),
                            "type": "main"
                        })
        
        # Thumbnail images
        for thumb in soup.select("[data-csa-c-item-id*='thumb'] img, .a-thumb-nail img"):
            if thumb.get('src'):
                images.append({
                    "url": urljoin(self.base_url, thumb['src']),
                    "alt": thumb.get('alt', ''),
                    "type": "thumbnail"
                })
        
        return images
    
    def _extract_pricing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pricing information"""
        pricing = {}
        
        # Current price
        price_selectors = [
            ".a-price-whole",
            ".a-offscreen",
            "[data-a-price-amount]",
            ".a-price .a-offscreen"
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text().strip()
                if '$' in price_text:
                    pricing['current_price'] = price_text
                    break
        
        # List price / was price
        list_price_elem = soup.select_one(".a-price.a-text-price .a-offscreen")
        if list_price_elem:
            pricing['list_price'] = list_price_elem.get_text().strip()
        
        # Savings
        savings_elem = soup.select_one(".savingsPercentage")
        if savings_elem:
            pricing['savings'] = savings_elem.get_text().strip()
        
        # Price per unit
        unit_price_elem = soup.select_one("[data-a-size='small'] .a-price")
        if unit_price_elem:
            pricing['unit_price'] = unit_price_elem.get_text().strip()
        
        return pricing
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract technical specifications"""
        specs = {}
        
        # Product details table
        detail_bullets = soup.select("#feature-bullets ul li span")
        for bullet in detail_bullets:
            text = bullet.get_text().strip()
            if ':' in text:
                key, value = text.split(':', 1)
                specs[key.strip()] = value.strip()
        
        # Technical details section
        tech_table = soup.select("#productDetails_techSpec_section_1 tr")
        for row in tech_table:
            cells = row.select('td')
            if len(cells) == 2:
                key = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                specs[key] = value
        
        # Additional information table
        additional_table = soup.select("#productDetails_detailBullets_sections1 tr")
        for row in additional_table:
            cells = row.select('td')
            if len(cells) == 2:
                key = cells[0].get_text().strip()
                value = cells[1].get_text().strip()
                specs[key] = value
        
        return specs
    
    def _extract_product_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed product information"""
        details = {}
        
        # Dimensions
        dimensions_patterns = [
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inches',
            r'(\d+\.?\d*)\s*"\s*x\s*(\d+\.?\d*)\s*"\s*x\s*(\d+\.?\d*)\s*"'
        ]
        
        page_text = soup.get_text()
        for pattern in dimensions_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                details['dimensions'] = {
                    'length': match.group(1),
                    'width': match.group(2),
                    'height': match.group(3),
                    'unit': 'inches'
                }
                break
        
        # Weight
        weight_match = re.search(r'(\d+\.?\d*)\s*(pounds?|lbs?|kg)', page_text, re.IGNORECASE)
        if weight_match:
            details['weight'] = {
                'value': weight_match.group(1),
                'unit': weight_match.group(2)
            }
        
        # Model number
        model_patterns = [
            r'Model Number:\s*([A-Z0-9\-]+)',
            r'Item model number:\s*([A-Z0-9\-]+)'
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                details['model_number'] = match.group(1)
                break
        
        return details
    
    def _extract_feature_bullets(self, soup: BeautifulSoup) -> List[str]:
        """Extract feature bullet points"""
        bullets = []
        
        # Feature bullets section
        feature_section = soup.select("#feature-bullets ul li")
        for li in feature_section:
            span = li.select_one("span")
            if span:
                text = span.get_text().strip()
                if text and not text.startswith("Make sure"):
                    bullets.append(text)
        
        return bullets
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract product categories"""
        categories = []
        
        # Breadcrumb navigation
        breadcrumbs = soup.select("#wayfinding-breadcrumbs_feature_div a")
        for breadcrumb in breadcrumbs:
            category = breadcrumb.get_text().strip()
            if category and category not in categories:
                categories.append(category)
        
        return categories
    
    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract breadcrumb navigation"""
        breadcrumbs = []
        
        breadcrumb_links = soup.select("#wayfinding-breadcrumbs_feature_div a")
        for link in breadcrumb_links:
            breadcrumbs.append({
                "text": link.get_text().strip(),
                "url": urljoin(self.base_url, link.get('href', ''))
            })
        
        return breadcrumbs
    
    def _extract_review_summary(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract review and rating information"""
        reviews = {}
        
        # Average rating
        rating_elem = soup.select_one("[data-hook='average-star-rating'] .a-icon-alt")
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                reviews['average_rating'] = float(rating_match.group(1))
        
        # Total reviews count
        review_count_elem = soup.select_one("#acrCustomerReviewText")
        if review_count_elem:
            count_text = review_count_elem.get_text()
            count_match = re.search(r'([\d,]+)', count_text)
            if count_match:
                reviews['total_reviews'] = int(count_match.group(1).replace(',', ''))
        
        # Rating breakdown
        rating_bars = soup.select("[data-hook='histogram-row']")
        rating_breakdown = {}
        for bar in rating_bars:
            star_elem = bar.select_one(".a-size-base")
            percent_elem = bar.select_one(".a-size-base:last-child")
            if star_elem and percent_elem:
                star = star_elem.get_text().strip()
                percent = percent_elem.get_text().strip()
                rating_breakdown[star] = percent
        
        if rating_breakdown:
            reviews['rating_breakdown'] = rating_breakdown
        
        return reviews
    
    def _extract_availability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract availability information"""
        availability = {}
        
        # Stock status
        stock_selectors = [
            "#availability span",
            "[data-hook='availability-info']",
            "#outOfStock"
        ]
        
        for selector in stock_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                if text:
                    availability['status'] = text
                    availability['in_stock'] = 'in stock' in text.lower()
                    break
        
        return availability
    
    def _extract_shipping_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract shipping information"""
        shipping = {}
        
        # Delivery info
        delivery_elem = soup.select_one("#deliveryBlockMessage, [data-hook='delivery-time']")
        if delivery_elem:
            shipping['delivery_info'] = delivery_elem.get_text().strip()
        
        # Prime delivery
        prime_elem = soup.select_one(".a-icon-prime")
        if prime_elem:
            shipping['prime_eligible'] = True
        
        return shipping
    
    def _extract_variations(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract product variations (size, color, etc.)"""
        variations = {}
        
        # Size variations
        size_elements = soup.select("[data-dp-url*='th=1'] .selection")
        if size_elements:
            variations['sizes'] = [elem.get_text().strip() for elem in size_elements]
        
        # Color variations
        color_elements = soup.select("[data-defaultasin] [title]")
        if color_elements:
            variations['colors'] = [elem.get('title') for elem in color_elements if elem.get('title')]
        
        return variations
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description"""
        # Product description sections
        desc_selectors = [
            "#productDescription p",
            "#aplus_feature_div",
            "[data-hook='product-description']"
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return None
    
    def _extract_videos(self, soup: BeautifulSoup) -> List[str]:
        """Extract product videos"""
        videos = []
        
        video_elements = soup.select("video source, [data-video-url]")
        for video in video_elements:
            video_url = video.get('src') or video.get('data-video-url')
            if video_url:
                videos.append(urljoin(self.base_url, video_url))
        
        return videos
    
    def _extract_warranty_info(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract warranty information"""
        warranty_text = soup.get_text()
        warranty_patterns = [
            r'warranty[:\s]+([^.]+)',
            r'guaranteed for (\d+ years?)',
            r'(\d+ year) warranty'
        ]
        
        for pattern in warranty_patterns:
            match = re.search(pattern, warranty_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_meta_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta data and SEO information"""
        meta_data = {}
        
        # Meta description
        meta_desc = soup.select_one("meta[name='description']")
        if meta_desc:
            meta_data['description'] = meta_desc.get('content', '')
        
        # Meta keywords
        meta_keywords = soup.select_one("meta[name='keywords']")
        if meta_keywords:
            meta_data['keywords'] = meta_keywords.get('content', '')
        
        # Canonical URL
        canonical = soup.select_one("link[rel='canonical']")
        if canonical:
            meta_data['canonical_url'] = canonical.get('href', '')
        
        return meta_data
    
    def _extract_related_products(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract related/recommended products"""
        related = []
        
        # "Frequently bought together" or similar sections
        related_selectors = [
            "[data-hook='buying-guide-item']",
            ".p13n-sc-truncated",
            "[data-asin] .s-link-style"
        ]
        
        for selector in related_selectors:
            for element in soup.select(selector):
                title_elem = element.select_one("h3, .s-size-mini")
                if title_elem:
                    title = title_elem.get_text().strip()
                    link = element.get('href') or element.select_one('a')
                    if link:
                        related.append({
                            "title": title,
                            "url": urljoin(self.base_url, link.get('href', ''))
                        })
        
        return related[:10]  # Limit to 10 related products


def parse_amazon_product(html_file_path: str, source_url: str = None) -> Dict[str, Any]:
    """
    Convenience function to parse Amazon product from HTML file
    """
    parser = AmazonProductParser()
    
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    return parser.parse(html_content, source_url)


def save_parsed_data(data: Dict[str, Any], output_path: str):
    """
    Save parsed data to JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage
    html_files = [
        "amazon_response.html",
        "amazon_response1.html"
    ]
    
    for html_file in html_files:
        try:
            print(f"Parsing {html_file}...")
            parsed_data = parse_amazon_product(html_file)
            
            # Create output filename
            output_file = f"parsed_{html_file.replace('.html', '.json')}"
            save_parsed_data(parsed_data, output_file)
            
            print(f"✅ Successfully parsed and saved to {output_file}")
            print(f"   ASIN: {parsed_data.get('asin', 'N/A')}")
            print(f"   Title: {parsed_data.get('title', 'N/A')[:80]}...")
            print(f"   Brand: {parsed_data.get('brand', 'N/A')}")
            print(f"   Specifications: {len(parsed_data.get('specifications', {}))} items")
            print()
            
        except Exception as e:
            print(f"❌ Error parsing {html_file}: {str(e)}")
