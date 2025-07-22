#!/usr/bin/env python3
"""
Complete Amazon Product Fetcher and Parser
Fetches product pages from Amazon.com and extracts comprehensive product data
Usage: python amazon_complete_fetcher_parser.py <asin_or_url>
"""

import requests
import json
import re
import sys
import os
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import random
from bs4 import BeautifulSoup
import hashlib

try:
    import curl_cffi.requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    print("⚠️  curl_cffi not available. Using standard requests (may be less reliable)")


class AmazonProductFetcher:
    """
    Fetches Amazon product pages with proper headers and anti-detection measures.
    """
    
    def __init__(self, use_curl_cffi=True):
        self.use_curl_cffi = use_curl_cffi and CURL_CFFI_AVAILABLE
        self.session = None
        if not self.use_curl_cffi:
            self.session = requests.Session()
        self.setup_headers()
    
    def setup_headers(self):
        """Setup realistic browser headers for Amazon.com requests."""
        self.headers = {
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
    
    def extract_asin_from_input(self, input_str: str) -> str:
        """
        Extract ASIN from various input formats.
        
        Args:
            input_str: ASIN, Amazon URL, or Amazon product link
            
        Returns:
            10-character ASIN
        """
        # Clean the input
        input_str = input_str.strip()
        
        # If it's already a 10-character ASIN
        if re.match(r'^[A-Z0-9]{10}$', input_str):
            return input_str
        
        # Extract ASIN from URL patterns
        asin_patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:/|\\?|$)'
        ]
        
        for pattern in asin_patterns:
            match = re.search(pattern, input_str)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract ASIN from input: {input_str}")
    
    def build_amazon_url(self, asin: str) -> str:
        """Build Amazon product URL from ASIN."""
        return f"https://www.amazon.com/dp/{asin}/"
    
    def fetch_product(self, asin_or_url: str, save_html: bool = False) -> str:
        """
        Fetch Amazon product page HTML.
        
        Args:
            asin_or_url: ASIN or Amazon product URL
            save_html: Whether to save HTML to file for debugging
            
        Returns:
            HTML content of the product page
        """
        try:
            # Extract ASIN and build URL
            asin = self.extract_asin_from_input(asin_or_url)
            url = self.build_amazon_url(asin)
            
            print(f"🛒 Fetching Amazon product...")
            print(f"📋 ASIN: {asin}")
            print(f"🌐 URL: {url}")
            print(f"⚙️  Method: {'curl_cffi' if self.use_curl_cffi else 'requests'}")
            print("-" * 60)
            
            # Add random delay to be respectful
            delay = random.uniform(2, 5)
            print(f"⏱️  Waiting {delay:.1f} seconds...")
            time.sleep(delay)
            
            # Make the request
            if self.use_curl_cffi:
                response = cf_requests.get(
                    url,
                    headers=self.headers,
                    impersonate="chrome120",
                    timeout=30
                )
            else:
                response = self.session.get(url, headers=self.headers, timeout=30)
            
            response.raise_for_status()
            
            print(f"✅ Successfully fetched page (Status: {response.status_code})")
            print(f"📊 Content size: {len(response.text):,} characters")
            
            # Check if we got a valid product page
            if self._is_valid_product_page(response.text):
                print(f"✅ Valid product page detected")
            else:
                print(f"⚠️  Page may be blocked or invalid")
            
            # Save HTML if requested
            if save_html:
                filename = f"amazon_product_{asin}_{int(time.time())}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 Saved HTML to: {filename}")
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch product page: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching product: {str(e)}")
    
    def _is_valid_product_page(self, html_content: str) -> bool:
        """Check if the fetched page is a valid Amazon product page."""
        # Check for common product page elements
        indicators = [
            'productTitle',
            'feature-bullets',
            'priceblock',
            'buybox',
            'add-to-cart'
        ]
        
        return any(indicator in html_content for indicator in indicators)


class EnhancedAmazonProductParser:
    """
    Enhanced Amazon product parser for comprehensive product specification extraction.
    Provides detailed product information extraction for cross-platform matching.
    """
    
    def __init__(self):
        self.base_url = "https://www.amazon.com"
        
    def parse(self, html_content: str, source_url: str = None) -> Dict[str, Any]:
        """
        Enhanced parsing function with additional matching features
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract ASIN from URL or page
        asin = self._extract_asin(soup, source_url)
        
        # Get basic product data
        basic_data = self._extract_basic_info(soup)
        
        # Enhanced data for matching
        enhanced_data = {
            "specifications": self._extract_comprehensive_specs(soup),
            "matching_data": self._extract_matching_identifiers(soup, basic_data),
            "physical_attributes": self._extract_physical_attributes_from_specs(soup),
            "performance_attributes": self._extract_performance_attributes(soup),
            "compatibility": self._extract_compatibility_info(soup),
            "materials": self._extract_materials_info(soup),
            "package_contents": self._extract_package_contents(soup),
            "certifications": self._extract_certifications(soup),
            "environmental": self._extract_environmental_info(soup),
            "usage_context": self._extract_usage_context(soup),
        }
        
        # Combine all data
        product_data = {
            **basic_data,
            **enhanced_data,
            "asin": asin,
            "source_url": source_url,
            "parsed_at": datetime.now().isoformat(),
        }
        
        # Generate fingerprint for matching
        product_data["fingerprint"] = self._generate_product_fingerprint(product_data)
        
        return product_data
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic product information"""
        return {
            "title": self._extract_title(soup),
            "brand": self._extract_brand(soup),
            "images": self._extract_images(soup),
            "pricing": self._extract_pricing(soup),
            "categories": self._extract_categories(soup),
            "breadcrumbs": self._extract_breadcrumbs(soup),
            "reviews": self._extract_review_summary(soup),
            "availability": self._extract_availability(soup),
            "shipping": self._extract_shipping_info(soup),
            "variations": self._extract_variations(soup),
            "description": self._extract_description(soup),
            "videos": self._extract_videos(soup),
            "warranty": self._extract_warranty_info(soup),
            "meta_data": self._extract_meta_data(soup),
            "related_products": self._extract_related_products(soup),
            "feature_bullets": self._extract_feature_bullets(soup)
        }
    
    def _extract_matching_identifiers(self, soup: BeautifulSoup, basic_data: Dict) -> Dict[str, Any]:
        """Extract identifiers useful for cross-platform matching"""
        identifiers = {}
        page_text = soup.get_text()
        
        # Model numbers
        model_patterns = [
            r'Model Number:?\s*([A-Z0-9\-_]+)',
            r'Item model number:?\s*([A-Z0-9\-_]+)',
            r'Part Number:?\s*([A-Z0-9\-_]+)',
            r'SKU:?\s*([A-Z0-9\-_]+)',
            r'Manufacturer Part Number:?\s*([A-Z0-9\-_]+)'
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                identifiers['model_number'] = match.group(1)
                break
        
        # UPC/EAN codes
        upc_patterns = [
            r'UPC:?\s*(\d{12})',
            r'EAN:?\s*(\d{13})',
            r'ISBN:?\s*(\d{10,13})'
        ]
        
        for pattern in upc_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                identifiers['barcode'] = match.group(1)
                break
        
        # Brand and title variations for fuzzy matching
        title = basic_data.get('title', '')
        brand = basic_data.get('brand', '')
        
        if title:
            clean_title = re.sub(r'[^\w\s]', ' ', title.lower())
            clean_title = ' '.join(clean_title.split())
            identifiers['clean_title'] = clean_title
            identifiers['title_keywords'] = self._extract_keywords_from_title(title)
        
        if brand:
            identifiers['brand_normalized'] = brand.lower().strip()
        
        return identifiers
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract meaningful keywords from product title"""
        stop_words = {
            'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'under', 'over'
        }
        
        clean_title = re.sub(r'[^\w\s]', ' ', title.lower())
        words = clean_title.split()
        
        keywords = []
        for word in words:
            if (len(word) > 2 and 
                word not in stop_words and 
                not word.isdigit() and
                not re.match(r'^\d+\w*$', word)):
                keywords.append(word)
        
        return keywords[:10]
    
    def _extract_comprehensive_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive specifications from all product detail sections"""
        all_specs = {}
        
        # Primary product details table
        primary_specs = self._extract_product_details_table(soup)
        all_specs.update(primary_specs)
        
        # Technical specifications table
        tech_specs = self._extract_technical_specs_table(soup)
        all_specs.update(tech_specs)
        
        # Feature bullets specifications
        feature_specs = self._extract_feature_bullets_specs(soup)
        all_specs.update(feature_specs)
        
        # Additional information tables
        additional_specs = self._extract_additional_info_tables(soup)
        all_specs.update(additional_specs)
        
        return all_specs
    
    def _extract_product_details_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract from the main product details table"""
        specs = {}
        
        table_selectors = [
            "#productDetails_detailBullets_sections1 tr",
            "#productDetails_detailBullets_sections2 tr",
            ".prodDetTable tr",
            "[id*='productDetails'] table tr"
        ]
        
        for selector in table_selectors:
            rows = soup.select(selector)
            for row in rows:
                th_elem = row.select_one('th')
                td_elem = row.select_one('td')
                
                if th_elem and td_elem:
                    key = th_elem.get_text().strip()
                    value = td_elem.get_text().strip()
                    value = ' '.join(value.split())
                    
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
                
                elif len(row.select('td')) == 2:
                    cells = row.select('td')
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    value = ' '.join(value.split())
                    
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
        
        return specs
    
    def _extract_technical_specs_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract from technical specifications tables"""
        specs = {}
        
        tech_selectors = [
            "#productDetails_techSpec_section_1 tr",
            "#tech-spec-table tr",
            ".tech-specs-table tr",
            "[id*='techSpec'] tr"
        ]
        
        for selector in tech_selectors:
            rows = soup.select(selector)
            for row in rows:
                cells = row.select('td, th')
                if len(cells) == 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    value = ' '.join(value.split())
                    
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
        
        return specs
    
    def _extract_feature_bullets_specs(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from feature bullets"""
        specs = {}
        
        bullet_elements = soup.select("#feature-bullets ul li span, .feature span")
        
        for bullet in bullet_elements:
            text = bullet.get_text().strip()
            
            if ':' in text and len(text) < 200:
                parts = text.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    value = ' '.join(value.split())
                    
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
        
        return specs
    
    def _extract_additional_info_tables(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract from additional information tables"""
        specs = {}
        
        additional_selectors = [
            ".a-keyvalue tr",
            ".comparison-table tr",
            "[class*='detail'] table tr",
            ".product-facts tr"
        ]
        
        for selector in additional_selectors:
            rows = soup.select(selector)
            for row in rows:
                cells = row.select('td, th')
                if len(cells) == 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    value = ' '.join(value.split())
                    
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
        
        return specs
    
    def _is_skip_entry(self, key: str, value: str) -> bool:
        """Determine if a specification entry should be skipped"""
        skip_patterns = [
            len(value.strip()) < 2,
            'see top 100' in value.lower(),
            'click here' in value.lower(),
            'javascript:' in value.lower(),
            'out of 5 stars' in value.lower(),
            key.lower() in ['customer reviews', 'best sellers rank', 'feedback'],
            value.startswith('data:'),
            'href=' in value,
            '<' in value and '>' in value
        ]
        
        return any(skip_patterns)
    
    def _extract_physical_attributes_from_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract physical attributes from comprehensive specifications"""
        attributes = {}
        specs = self._extract_comprehensive_specs(soup)
        
        # Extract dimensions
        dimension_keys = [
            'Product Dimensions', 'Dimensions', 'Size', 'Item Dimensions',
            'Package Dimensions', 'Overall Dimensions'
        ]
        
        for key in dimension_keys:
            if key in specs:
                dim_text = specs[key]
                patterns = [
                    r'(\d+\.?\d*)"?D\s*x\s*(\d+\.?\d*)"?W\s*x\s*(\d+\.?\d*)"?H',
                    r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inches',
                    r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, dim_text, re.IGNORECASE)
                    if match:
                        attributes['dimensions'] = {
                            'length': float(match.group(1)),
                            'width': float(match.group(2)),
                            'height': float(match.group(3)),
                            'unit': 'inches',
                            'original_text': dim_text
                        }
                        break
                
                if 'dimensions' in attributes:
                    break
        
        # Extract weight
        weight_keys = ['Item Weight', 'Weight', 'Shipping Weight', 'Product Weight']
        for key in weight_keys:
            if key in specs:
                weight_text = specs[key]
                weight_match = re.search(r'(\d+\.?\d*)\s*(pounds?|lbs?|kg|grams?)', weight_text, re.IGNORECASE)
                if weight_match:
                    attributes['weight'] = {
                        'value': float(weight_match.group(1)),
                        'unit': weight_match.group(2).lower(),
                        'original_text': weight_text
                    }
                    break
        
        # Extract color
        if 'Color' in specs:
            attributes['color'] = specs['Color']
        
        # Extract material
        material_keys = ['Material', 'Fabric Type', 'Construction Material', 'Frame Material']
        for key in material_keys:
            if key in specs:
                attributes['material'] = specs[key]
                break
        
        return attributes
    
    def _extract_performance_attributes(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract performance-related attributes"""
        attributes = {}
        page_text = soup.get_text()
        
        # Energy efficiency
        energy_patterns = [
            r'Energy Star',
            r'(\d+)\s*stars?',
            r'Energy Efficiency:?\s*([A-Z\+\-]+)',
            r'(\d+\.?\d*)\s*kWh'
        ]
        
        for pattern in energy_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                attributes['energy_info'] = match.group(0)
                break
        
        return attributes
    
    def _extract_compatibility_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract compatibility information"""
        compatibility = {}
        page_text = soup.get_text()
        
        compatibility_patterns = [
            r'Compatible with:?\s*([^.]+)',
            r'Works with:?\s*([^.]+)',
            r'Fits:?\s*([^.]+)',
            r'Designed for:?\s*([^.]+)'
        ]
        
        for pattern in compatibility_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                compat_text = match.group(1)
                compatibility['devices'] = [item.strip() for item in re.split(r'[,;]', compat_text)]
                break
        
        return compatibility
    
    def _extract_materials_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract materials and construction information"""
        materials = {}
        page_text = soup.get_text()
        
        material_patterns = [
            r'Material:?\s*([^.]+)',
            r'Made of:?\s*([^.]+)',
            r'Construction:?\s*([^.]+)',
            r'Fabric:?\s*([^.]+)',
            r'Frame:?\s*([^.]+)'
        ]
        
        for pattern in material_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                material_type = pattern.split(':')[0].strip('r\'').lower()
                materials[material_type] = match.group(1).strip()
        
        return materials
    
    def _extract_package_contents(self, soup: BeautifulSoup) -> List[str]:
        """Extract what's included in the package"""
        contents = []
        page_text = soup.get_text()
        
        package_patterns = [
            r'Package includes?:?\s*([^.]+)',
            r'What\'s in the box:?\s*([^.]+)',
            r'Includes?:?\s*([^.]+)',
            r'Contents?:?\s*([^.]+)'
        ]
        
        for pattern in package_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                content_text = match.group(1)
                contents = [item.strip() for item in re.split(r'[,;]', content_text)]
                break
        
        return contents
    
    def _extract_certifications(self, soup: BeautifulSoup) -> List[str]:
        """Extract certifications and standards"""
        certifications = []
        page_text = soup.get_text()
        
        cert_patterns = [
            r'CE certified',
            r'FCC approved',
            r'Energy Star',
            r'UL listed',
            r'FDA approved',
            r'ISO \d+',
            r'RoHS compliant'
        ]
        
        for pattern in cert_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                certifications.append(pattern)
        
        return certifications
    
    def _extract_environmental_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract environmental and sustainability information"""
        environmental = {}
        page_text = soup.get_text()
        
        env_patterns = [
            r'recyclable',
            r'eco-?friendly',
            r'sustainable',
            r'biodegradable',
            r'green',
            r'renewable'
        ]
        
        for pattern in env_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                environmental['eco_friendly'] = True
                break
        
        return environmental
    
    def _extract_usage_context(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract usage context and applications"""
        context = {}
        title = self._extract_title(soup) or ""
        desc = self._extract_description(soup) or ""
        
        room_keywords = ['living room', 'bedroom', 'kitchen', 'bathroom', 'office', 'outdoor', 'garage', 'basement']
        rooms = [room for room in room_keywords if room.lower() in (title + " " + desc).lower()]
        if rooms:
            context['rooms'] = rooms
        
        use_keywords = ['gaming', 'work', 'exercise', 'cooking', 'cleaning', 'storage', 'decoration']
        uses = [use for use in use_keywords if use.lower() in (title + " " + desc).lower()]
        if uses:
            context['use_cases'] = uses
        
        return context
    
    def _generate_product_fingerprint(self, product_data: Dict[str, Any]) -> str:
        """Generate a fingerprint for product matching"""
        fingerprint_data = {
            'brand': product_data.get('brand', '').lower(),
            'clean_title': product_data.get('matching_data', {}).get('clean_title', ''),
            'model_number': product_data.get('matching_data', {}).get('model_number', ''),
            'dimensions': product_data.get('physical_attributes', {}).get('dimensions', {}),
            'weight': product_data.get('physical_attributes', {}).get('weight', {})
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def _extract_asin(self, soup: BeautifulSoup, source_url: str = None) -> Optional[str]:
        """Extract ASIN from URL or page content"""
        if source_url:
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', source_url)
            if asin_match:
                return asin_match.group(1)
        
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
        byline = soup.select_one("#bylineInfo")
        if byline:
            brand_text = byline.get_text().strip()
            if "Visit the" in brand_text and "Store" in brand_text:
                return brand_text.replace("Visit the", "").replace("Store", "").strip()
        
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
        
        return images
    
    def _extract_pricing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pricing information"""
        pricing = {}
        
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
        
        return pricing
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract product categories"""
        categories = []
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
        
        rating_elem = soup.select_one("[data-hook='average-star-rating'] .a-icon-alt")
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                reviews['average_rating'] = float(rating_match.group(1))
        
        review_count_elem = soup.select_one("#acrCustomerReviewText")
        if review_count_elem:
            count_text = review_count_elem.get_text()
            count_match = re.search(r'([\d,]+)', count_text)
            if count_match:
                reviews['total_reviews'] = int(count_match.group(1).replace(',', ''))
        
        return reviews
    
    def _extract_availability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract availability information"""
        availability = {}
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
        delivery_elem = soup.select_one("#deliveryBlockMessage, [data-hook='delivery-time']")
        if delivery_elem:
            shipping['delivery_info'] = delivery_elem.get_text().strip()
        
        prime_elem = soup.select_one(".a-icon-prime")
        if prime_elem:
            shipping['prime_eligible'] = True
        
        return shipping
    
    def _extract_variations(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract product variations"""
        variations = {}
        size_elements = soup.select("[data-dp-url*='th=1'] .selection")
        if size_elements:
            variations['sizes'] = [elem.get_text().strip() for elem in size_elements]
        
        color_elements = soup.select("[data-defaultasin] [title]")
        if color_elements:
            variations['colors'] = [elem.get('title') for elem in color_elements if elem.get('title')]
        
        return variations
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description"""
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
        """Extract meta data"""
        meta_data = {}
        
        meta_desc = soup.select_one("meta[name='description']")
        if meta_desc:
            meta_data['description'] = meta_desc.get('content', '')
        
        canonical = soup.select_one("link[rel='canonical']")
        if canonical:
            meta_data['canonical_url'] = canonical.get('href', '')
        
        return meta_data
    
    def _extract_related_products(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract related products"""
        related = []
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
        
        return related[:10]
    
    def _extract_feature_bullets(self, soup: BeautifulSoup) -> List[str]:
        """Extract feature bullets"""
        bullets = []
        feature_section = soup.select("#feature-bullets ul li")
        for li in feature_section:
            span = li.select_one("span")
            if span:
                text = span.get_text().strip()
                if text and not text.startswith("Make sure"):
                    bullets.append(text)
        return bullets
    
    def get_comparison_data(self) -> Dict[str, Any]:
        """
        Get standardized data for cross-platform product comparison.
        Returns key fields in a consistent format for matching with other platforms.
        """
        if not hasattr(self, 'extracted_data') or not self.extracted_data:
            return {}
        
        basic = self.extracted_data
        physical = basic.get("physical_attributes", {})
        pricing = basic.get("pricing", {})
        matching = basic.get("matching_data", {})
        
        return {
            "platform": "Amazon",
            "product_id": basic.get("asin"),
            "name": basic.get("title"),
            "brand": basic.get("brand"),
            "model": matching.get("model_number"),
            "upc": matching.get("barcode"),
            "gtin": matching.get("barcode"),
            "current_price": pricing.get("current_price"),
            "regular_price": pricing.get("list_price"),
            "dimensions": {
                "length": physical.get("dimensions", {}).get("length"),
                "width": physical.get("dimensions", {}).get("width"),
                "height": physical.get("dimensions", {}).get("height"),
                "weight": physical.get("weight", {}).get("value"),
                "unit": physical.get("dimensions", {}).get("unit")
            },
            "features": basic.get("feature_bullets", []),
            "materials": list(basic.get("materials", {}).values()),
            "specifications": basic.get("specifications", {}),
            "total_specs": len(basic.get("specifications", {})),
            "extraction_source": "amazon_complete_fetcher_parser.py"
        }


class AmazonProductExtractor:
    """
    Complete Amazon product extraction system that combines fetching and parsing.
    """
    
    def __init__(self, save_html: bool = False, save_json: bool = True, use_curl_cffi: bool = True):
        self.fetcher = AmazonProductFetcher(use_curl_cffi=use_curl_cffi)
        self.parser = EnhancedAmazonProductParser()
        self.save_html = save_html
        self.save_json = save_json
    
    def extract_product(self, asin_or_url: str) -> Dict[str, Any]:
        """
        Complete product extraction from Amazon ASIN or URL.
        
        Args:
            asin_or_url: Amazon ASIN or product URL
            
        Returns:
            Complete product specifications dictionary
        """
        try:
            print(f"🛒 Starting Amazon product extraction...")
            print(f"📋 Input: {asin_or_url}")
            print(f"⚙️  Settings: Save HTML={self.save_html}, Save JSON={self.save_json}")
            print("-" * 60)
            
            # Step 1: Fetch the product page
            html_content = self.fetcher.fetch_product(asin_or_url, save_html=self.save_html)
            
            # Step 2: Parse the HTML content
            print(f"\n🔍 Parsing product data...")
            asin = self.fetcher.extract_asin_from_input(asin_or_url)
            url = self.fetcher.build_amazon_url(asin)
            product_data = self.parser.parse(html_content, source_url=url)
            
            if "error" in product_data:
                print(f"❌ Parsing failed: {product_data['error']}")
                return product_data
            
            # Store extracted data for comparison methods
            self.parser.extracted_data = product_data
            
            # Step 3: Save JSON if requested
            if self.save_json:
                timestamp = int(time.time())
                asin = product_data.get("asin", "unknown")
                filename = f"amazon_product_{asin}_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(product_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved product data to: {filename}")
            
            # Step 4: Display summary
            self._display_summary(product_data)
            
            return product_data
            
        except Exception as e:
            error_msg = f"Failed to extract product: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _display_summary(self, product_data: Dict):
        """Display a formatted summary of extracted product data."""
        print(f"\n" + "=" * 60)
        print(f"🛒 AMAZON PRODUCT EXTRACTION COMPLETE")
        print(f"=" * 60)
        
        pricing = product_data.get("pricing", {})
        physical = product_data.get("physical_attributes", {})
        reviews = product_data.get("reviews", {})
        matching = product_data.get("matching_data", {})
        
        print(f"📦 Product: {product_data.get('title', 'N/A')}")
        print(f"🏷️  Brand: {product_data.get('brand', 'N/A')}")
        print(f"🆔 ASIN: {product_data.get('asin', 'N/A')}")
        print(f"🔢 Model: {matching.get('model_number', 'N/A')}")
        print(f"🔢 UPC: {matching.get('barcode', 'N/A')}")
        print(f"💰 Price: {pricing.get('current_price', 'N/A')}")
        if pricing.get('list_price'):
            print(f"   List Price: {pricing.get('list_price', 'N/A')}")
            if pricing.get('savings'):
                print(f"   Savings: {pricing.get('savings', 'N/A')}")
        
        # Display dimensions
        dimensions = physical.get('dimensions', {})
        if dimensions:
            print(f"📏 Dimensions: {dimensions.get('length')} x {dimensions.get('width')} x {dimensions.get('height')} {dimensions.get('unit', '')}")
        
        # Display weight
        weight = physical.get('weight', {})
        if weight:
            print(f"⚖️  Weight: {weight.get('value')} {weight.get('unit', '')}")
        
        print(f"⭐ Rating: {reviews.get('average_rating', 'N/A')} ({reviews.get('total_reviews', 0)} reviews)")
        print(f"📊 Total Specifications: {len(product_data.get('specifications', {}))}")
        
        # Show top specifications
        specs = product_data.get("specifications", {})
        if specs:
            print(f"\n🔧 Key Specifications:")
            for key, value in list(specs.items())[:5]:
                print(f"   • {key}: {value}")
            if len(specs) > 5:
                print(f"   ... and {len(specs) - 5} more")
        
        # Show top features
        features = product_data.get("feature_bullets", [])
        if features:
            print(f"\n✨ Key Features:")
            for feature in features[:3]:
                print(f"   • {feature[:80]}{'...' if len(feature) > 80 else ''}")
            if len(features) > 3:
                print(f"   ... and {len(features) - 3} more features")
        
        # Show variations
        variations = product_data.get("variations", {})
        if variations.get('colors'):
            print(f"\n🎨 Available Colors: {len(variations['colors'])} options")
        if variations.get('sizes'):
            print(f"📏 Available Sizes: {len(variations['sizes'])} options")
        
        print(f"\n✅ Extraction completed successfully!")
        print(f"🕐 Timestamp: {product_data.get('parsed_at', 'N/A')}")
        print(f"🔍 Fingerprint: {product_data.get('fingerprint', 'N/A')[:16]}...")
        print(f"=" * 60)


def main():
    """Main function for command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python amazon_complete_fetcher_parser.py <asin_or_url>")
        print("Examples:")
        print("  python amazon_complete_fetcher_parser.py B00FS3VJAO")
        print("  python amazon_complete_fetcher_parser.py 'https://www.amazon.com/dp/B00FS3VJAO/'")
        sys.exit(1)
    
    asin_or_url = sys.argv[1]
    
    # Create extractor with default settings
    extractor = AmazonProductExtractor(save_html=True, save_json=True, use_curl_cffi=True)
    
    # Extract product
    result = extractor.extract_product(asin_or_url)
    
    if "error" in result:
        sys.exit(1)
    
    print(f"\n🎉 Product extraction completed successfully!")


def demo_with_example():
    """Demo function with example ASIN."""
    example_asin = "B00FS3VJAO"
    
    print("🛒 Amazon Product Fetcher & Parser Demo")
    print("=" * 50)
    
    extractor = AmazonProductExtractor(save_html=True, save_json=True, use_curl_cffi=True)
    result = extractor.extract_product(example_asin)
    
    if "error" not in result:
        print(f"\n📊 Comparison Data Available:")
        comparison_data = extractor.parser.get_comparison_data()
        print(f"   Platform: {comparison_data.get('platform')}")
        print(f"   Product ID: {comparison_data.get('product_id')}")
        print(f"   Specifications Count: {comparison_data.get('total_specs')}")
        print(f"   Ready for Cross-Platform Matching: ✅")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Run demo if no arguments provided
        demo_with_example()
    else:
        # Run with provided ASIN/URL
        main()
