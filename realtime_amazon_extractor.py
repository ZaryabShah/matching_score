#!/usr/bin/env python3
"""
Real-time Amazon Product Extractor and Parser

This script combines scraping and parsing functionality to extract and analyze
Amazon product data in real-time based on user-provided keywords.
"""

import os
import re
import json
import time
import html
import statistics
from datetime import datetime
from typing import List, Dict, Optional, Union
from collections import Counter
from urllib.parse import quote_plus

# Import parsing dependencies
from bs4 import BeautifulSoup

# Import scraping dependencies
from curl_cffi import requests


class RealTimeAmazonExtractor:
    """
    Real-time Amazon product extractor and parser that combines scraping
    and parsing functionality for immediate keyword-based product analysis.
    """
    
    def __init__(self, proxy_config: Optional[Dict] = None):
        """
        Initialize the real-time extractor.
        
        Args:
            proxy_config (Dict, optional): Proxy configuration with 'url' key
        """
        self.proxy_config = proxy_config or {}
        self.products = []
        self.metadata = {}
        self.scraping_config = self._setup_scraping_config()
        
    def _setup_scraping_config(self):
        """Setup scraping configuration."""
        # Default proxy configuration
        default_proxy = "http://250621Ev04e-resi_region-US_California:5PjDM1IoS0JSr2c@ca.proxy-jet.io:1010"
        
        proxy_url = self.proxy_config.get('url', default_proxy)
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        } if proxy_url else {}
        
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "device-memory": "8",
            "downlink": "1.4",
            "dpr": "1.5",
            "ect": "3g",
            "priority": "u=0, i",
            "rtt": "300",
            "sec-ch-device-memory": "8",
            "sec-ch-dpr": "1.5",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"10.0.0"',
            "sec-ch-viewport-width": "1280",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "viewport-width": "1280",
            "cookie": "csm-sid=914-9361493-3807925; x-amz-captcha-1=1753048012390900; x-amz-captcha-2=NMEeDcMCIdStulUDaEttPQ==; session-id=132-5048832-5252361; session-id-time=2082787201l; i18n-prefs=USD; lc-main=en_US; skin=noskin; ubid-main=134-3385365-1946806; session-token=i/AAXFcG1DGH38MqdJfJv6ri0S8N321KicL0yguouNfD0BOAn6bVlTwjItERn9jX7rMZSk0OAnB2mlSZImNOASzhRTA+lSjOfz7qelyhD1Y26wu4EckKBtF1iht3OC2hrkq9wX2eU7wcd1EVIHrgbLZGYe/+NMJxuAIwXcNs90zvTKnzZKc5ISKLbmcWRLq0tRj2coiI+EUPlEOr81a/WLnoxrWP+5eZj3Hj/CgZBvUKUGLDwgKb3I/4u/SB8zEYYDnjs+BaTLRzckU/Db/S+P2iruLsJOXlaRS5cloGw5lR05rgRaCQUYDYds92upj8LCxWM6RsVCDQv8B16NwWbTC/UKkQ8pXt; csm-hit=tb:AXJYQAC8NK0DP9EGGP47+s-AXJYQAC8NK0DP9EGGP47|1753041291657&t:1753041291657&adb:adblk_no; rxc=AMPob19TK6Z0WVPM4ZU"
        }
        
        return {
            'headers': headers,
            'proxies': proxies,
            'timeout': 30
        }
    
    def search_and_extract(self, keyword: str, max_pages: int = 1, delay: float = 2.0) -> Dict:
        """
        Search Amazon for a keyword and extract product data in real-time.
        
        Args:
            keyword (str): Search keyword
            max_pages (int): Maximum pages to scrape (default: 1)
            delay (float): Delay between requests in seconds (default: 2.0)
            
        Returns:
            Dict: Complete extraction results with products and metadata
        """
        print(f"🔍 Starting real-time extraction for keyword: '{keyword}'")
        print(f"📄 Max pages: {max_pages}, Delay: {delay}s")
        print("-" * 60)
        
        all_products = []
        extraction_stats = {
            'keyword': keyword,
            'pages_scraped': 0,
            'total_products': 0,
            'scraping_errors': 0,
            'parsing_errors': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        for page in range(1, max_pages + 1):
            print(f"\n📃 Processing page {page}/{max_pages}...")
            
            try:
                # Scrape the page
                html_content = self._scrape_page(keyword, page)
                if not html_content:
                    print(f"❌ Failed to scrape page {page}")
                    extraction_stats['scraping_errors'] += 1
                    continue
                
                print(f"✅ Successfully scraped page {page}")
                
                # Parse the content
                page_products = self._parse_html_content(html_content, keyword)
                if page_products:
                    all_products.extend(page_products)
                    print(f"📦 Extracted {len(page_products)} products from page {page}")
                else:
                    print(f"⚠️ No products found on page {page}")
                    extraction_stats['parsing_errors'] += 1
                
                extraction_stats['pages_scraped'] += 1
                
                # Delay between requests (except for last page)
                if page < max_pages:
                    print(f"⏳ Waiting {delay}s before next page...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Error processing page {page}: {str(e)}")
                extraction_stats['scraping_errors'] += 1
                continue
        
        # Update final stats
        extraction_stats['total_products'] = len(all_products)
        extraction_stats['end_time'] = datetime.now().isoformat()
        
        # Create final result
        result = {
            'products': all_products,
            'metadata': {
                'search_keyword': keyword,
                'total_products_found': len(all_products),
                'extraction_timestamp': datetime.now().isoformat(),
                'extraction_stats': extraction_stats
            },
            'summary': self._generate_summary(all_products)
        }
        
        self.products = all_products
        self.metadata = result['metadata']
        
        print(f"\n🎉 Extraction completed!")
        print(f"📊 Total products extracted: {len(all_products)}")
        print(f"📈 Success rate: {extraction_stats['pages_scraped']}/{max_pages} pages")
        
        return result
    
    def _scrape_page(self, keyword: str, page: int = 1) -> Optional[str]:
        """Scrape a single Amazon search results page."""
        try:
            # Encode the keyword for URL
            encoded_keyword = quote_plus(keyword)
            
            # Build the search URL
            if page == 1:
                url = f"https://www.amazon.com/s?k={encoded_keyword}"
            else:
                url = f"https://www.amazon.com/s?k={encoded_keyword}&page={page}"
            
            print(f"🌐 Requesting: {url}")
            
            # Make the request
            response = requests.get(
                url,
                headers=self.scraping_config['headers'],
                proxies=self.scraping_config['proxies'],
                impersonate="chrome120",
                timeout=self.scraping_config['timeout']
            )
            
            if response.status_code == 200:
                print(f"✅ HTTP {response.status_code} - Content length: {len(response.text)} chars")
                return response.text
            else:
                print(f"❌ HTTP {response.status_code} - Request failed")
                return None
                
        except requests.RequestsError as e:
            print(f"❌ Request error: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return None
    
    def _parse_html_content(self, html_content: str, keyword: str) -> List[Dict]:
        """Parse HTML content and extract product data."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all product containers
            product_containers = soup.find_all('div', {
                'role': 'listitem',
                'data-component-type': 's-search-result'
            })
            
            print(f"🔍 Found {len(product_containers)} product containers")
            
            products = []
            for i, container in enumerate(product_containers):
                try:
                    product_data = self._extract_product_data(container)
                    if product_data and product_data.get('asin'):
                        products.append(product_data)
                        print(f"  ✓ Product {i+1}: {product_data.get('title', {}).get('short_title', 'N/A')}")
                    else:
                        print(f"  ⚠ Product {i+1}: Failed to extract valid data")
                except Exception as e:
                    print(f"  ❌ Product {i+1}: Error - {str(e)}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"❌ HTML parsing error: {str(e)}")
            return []
    
    def _extract_product_data(self, container) -> Optional[Dict]:
        """Extract comprehensive product data from a product container."""
        try:
            product = {}
            
            # Basic identifiers
            product['asin'] = container.get('data-asin', '')
            product['data_index'] = container.get('data-index', '')
            product['data_uuid'] = container.get('data-uuid', '')
            
            # Product title
            product['title'] = self._extract_title(container)
            
            # Brand information
            product['brand'] = self._extract_brand(container)
            
            # Price information
            product['pricing'] = self._extract_pricing(container)
            
            # Images
            product['images'] = self._extract_images(container)
            
            # Rating and reviews
            product['reviews'] = self._extract_reviews(container)
            
            # Product links
            product['links'] = self._extract_links(container)
            
            # Availability and shipping
            product['shipping'] = self._extract_shipping_info(container)
            
            # Product features and variants
            product['variants'] = self._extract_variants(container)
            
            # Categories and tags
            product['categories'] = self._extract_categories(container)
            
            # Sponsored/ad information
            product['advertising'] = self._extract_ad_info(container)
            
            # Product badges and certifications
            product['badges'] = self._extract_badges(container)
            
            # Additional metadata
            product['metadata'] = self._extract_product_metadata(container)
            
            return product
            
        except Exception as e:
            print(f"Error extracting product data: {str(e)}")
            return None
    
    def _extract_title(self, container) -> Dict:
        """Extract product title information."""
        title_info = {'full_title': '', 'short_title': '', 'aria_label': ''}
        
        # Main title
        title_element = container.find('h2', class_=re.compile(r'a-size-\w+'))
        if title_element:
            span = title_element.find('span')
            if span:
                title_info['full_title'] = span.get_text(strip=True)
                title_info['aria_label'] = title_element.get('aria-label', '')
        
        # Alternative title extraction
        if not title_info['full_title']:
            title_link = container.find('a', class_=re.compile(r's-link-style'))
            if title_link:
                title_info['full_title'] = title_link.get_text(strip=True)
        
        # Create short title (first 50 characters)
        if title_info['full_title']:
            title_info['short_title'] = (title_info['full_title'][:50] + '...') if len(title_info['full_title']) > 50 else title_info['full_title']
        
        return title_info
    
    def _extract_brand(self, container) -> Dict:
        """Extract brand information."""
        brand_info = {'name': '', 'is_amazon_brand': False, 'is_sponsored': False}
        
        # Check for Amazon brand
        amazon_brand = container.find('span', string=re.compile(r'Featured from Amazon brands'))
        if amazon_brand:
            brand_info['is_amazon_brand'] = True
        
        # Check for sponsored content
        sponsored = container.find('span', string=re.compile(r'Sponsored|Featured'))
        if sponsored:
            brand_info['is_sponsored'] = True
        
        # Extract brand name from title (common patterns)
        title = self._extract_title(container)['full_title']
        if title:
            # Brand is often the first word(s) before product description
            words = title.split()
            if words:
                brand_info['name'] = words[0]
        
        return brand_info
    
    def _extract_pricing(self, container) -> Dict:
        """Extract comprehensive pricing information."""
        pricing = {
            'current_price': {},
            'original_price': {},
            'list_price': {},
            'discount': {},
            'currency': 'USD',
            'coupon': {},
            'prime_price': {}
        }
        
        # Current price
        price_span = container.find('span', class_='a-price')
        if price_span:
            price_text = price_span.find('span', class_='a-offscreen')
            if price_text:
                price_str = price_text.get_text(strip=True)
                pricing['current_price'] = self._parse_price(price_str)
        
        # Original/List price (strikethrough)
        original_price = container.find('span', {'data-a-strike': 'true'})
        if original_price:
            price_text = original_price.find('span', class_='a-offscreen')
            if price_text:
                pricing['original_price'] = self._parse_price(price_text.get_text(strip=True))
        
        # Coupon information
        coupon = container.find('span', class_=re.compile(r's-coupon'))
        if coupon:
            coupon_text = coupon.get_text(strip=True)
            pricing['coupon'] = {
                'available': True,
                'text': coupon_text,
                'amount': self._extract_coupon_amount(coupon_text)
            }
        
        return pricing
    
    def _parse_price(self, price_string: str) -> Dict:
        """Parse price string into components."""
        price_info = {'raw': price_string, 'amount': 0.0, 'currency': 'USD'}
        
        # Extract numeric value
        amount_match = re.search(r'[\d,]+\.?\d*', price_string.replace(',', ''))
        if amount_match:
            try:
                price_info['amount'] = float(amount_match.group().replace(',', ''))
            except ValueError:
                price_info['amount'] = 0.0
        
        # Extract currency symbol
        currency_match = re.search(r'[₹$€£¥₩]', price_string)
        if currency_match:
            currency_map = {'$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY', '₹': 'INR', '₩': 'KRW'}
            price_info['currency'] = currency_map.get(currency_match.group(), 'USD')
        
        return price_info
    
    def _extract_coupon_amount(self, coupon_text: str) -> float:
        """Extract coupon discount amount."""
        amount_match = re.search(r'[\d,]+\.?\d*', coupon_text)
        if amount_match:
            try:
                return float(amount_match.group().replace(',', ''))
            except ValueError:
                return 0.0
        return 0.0
    
    def _extract_images(self, container) -> Dict:
        """Extract image information."""
        images = {'primary': {}, 'thumbnails': [], 'variants': []}
        
        # Primary product image
        img_element = container.find('img', class_='s-image')
        if img_element:
            images['primary'] = {
                'url': img_element.get('src', ''),
                'alt_text': img_element.get('alt', ''),
                'srcset': img_element.get('srcset', ''),
                'dimensions': self._extract_image_dimensions(img_element.get('src', ''))
            }
        
        # Extract different image sizes from srcset
        if images['primary'].get('srcset'):
            srcset = images['primary']['srcset']
            image_variants = []
            for item in srcset.split(','):
                parts = item.strip().split(' ')
                if len(parts) >= 2:
                    image_variants.append({
                        'url': parts[0],
                        'density': parts[1]
                    })
            images['variants'] = image_variants
        
        return images
    
    def _extract_image_dimensions(self, image_url: str) -> Dict:
        """Extract image dimensions from URL pattern."""
        # Amazon image URLs often contain dimension info
        dimension_match = re.search(r'_(\d+)x(\d+)_', image_url)
        if dimension_match:
            return {
                'width': int(dimension_match.group(1)),
                'height': int(dimension_match.group(2))
            }
        
        # Alternative pattern
        alt_match = re.search(r'_UL(\d+)_', image_url)
        if alt_match:
            size = int(alt_match.group(1))
            return {'width': size, 'height': size}
        
        return {}
    
    def _extract_reviews(self, container) -> Dict:
        """Extract review and rating information."""
        reviews = {
            'rating': {},
            'count': 0,
            'rating_breakdown': {},
            'recent_activity': {}
        }
        
        # Star rating
        star_element = container.find('i', class_=re.compile(r'a-icon-star'))
        if star_element:
            alt_text = star_element.find('span', class_='a-icon-alt')
            if alt_text:
                rating_text = alt_text.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    reviews['rating'] = {
                        'value': float(rating_match.group(1)),
                        'scale': 5,
                        'text': rating_text
                    }
        
        # Review count
        rating_count = container.find('a', {'aria-label': re.compile(r'\d+\s+ratings?')})
        if rating_count:
            count_text = rating_count.get('aria-label', '')
            count_match = re.search(r'(\d+(?:,\d+)*)', count_text)
            if count_match:
                reviews['count'] = int(count_match.group(1).replace(',', ''))
        
        # Recent purchase activity
        recent_activity = container.find('span', string=re.compile(r'\d+\+?\s+bought in past'))
        if recent_activity:
            activity_text = recent_activity.get_text()
            reviews['recent_activity'] = {
                'text': activity_text,
                'timeframe': 'past_month' if 'month' in activity_text else 'recent'
            }
        
        return reviews
    
    def _extract_links(self, container) -> Dict:
        """Extract product links."""
        links = {
            'product_page': '',
            'reviews': '',
            'seller': '',
            'brand': ''
        }
        
        # Main product link
        main_link = container.find('a', class_=re.compile(r's-link-style'))
        if main_link:
            links['product_page'] = main_link.get('href', '')
        
        # Reviews link
        reviews_link = container.find('a', href=re.compile(r'#customerReviews'))
        if reviews_link:
            links['reviews'] = reviews_link.get('href', '')
        
        return links
    
    def _extract_shipping_info(self, container) -> Dict:
        """Extract shipping and delivery information."""
        shipping = {
            'free_shipping': False,
            'prime_eligible': False,
            'delivery_date': {},
            'shipping_cost': {},
            'delivery_options': []
        }
        
        # Free delivery information
        free_delivery = container.find(string=re.compile(r'FREE delivery|Free delivery'))
        if free_delivery:
            shipping['free_shipping'] = True
            
            # Extract delivery date
            delivery_date = container.find('span', {'id': re.compile(r'WVCRIAFWG')})
            if delivery_date:
                shipping['delivery_date']['primary'] = delivery_date.get_text(strip=True)
        
        # Fastest delivery option
        fastest_delivery = container.find(string=re.compile(r'fastest delivery|Or fastest'))
        if fastest_delivery:
            fastest_element = fastest_delivery.find_next('span', class_='a-text-bold')
            if fastest_element:
                shipping['delivery_date']['fastest'] = fastest_element.get_text(strip=True)
        
        # Prime eligibility (implied by free shipping usually)
        if shipping['free_shipping']:
            shipping['prime_eligible'] = True
        
        return shipping
    
    def _extract_variants(self, container) -> Dict:
        """Extract product variants (colors, sizes, etc.)."""
        variants = {
            'colors': [],
            'sizes': [],
            'patterns': [],
            'other_options': []
        }
        
        # Color swatches
        color_container = container.find('div', class_=re.compile(r's-color-swatch'))
        if color_container:
            color_links = color_container.find_all('a', {'aria-label': True})
            for link in color_links:
                color_name = link.get('aria-label', '')
                if color_name and color_name not in ['+', 'other']:
                    variants['colors'].append({
                        'name': color_name,
                        'url': link.get('href', ''),
                        'selected': 'aria-current' in link.attrs
                    })
        
        # Additional color options indicator
        more_colors = container.find('a', string=re.compile(r'\+\d+\s+other\s+colors'))
        if more_colors:
            more_text = more_colors.get_text()
            count_match = re.search(r'\+(\d+)', more_text)
            if count_match:
                variants['additional_options_count'] = int(count_match.group(1))
        
        return variants
    
    def _extract_categories(self, container) -> Dict:
        """Extract category and classification information."""
        categories = {
            'primary': '',
            'subcategories': [],
            'tags': [],
            'department': ''
        }
        
        # Category tags/badges
        category_badge = container.find('span', class_=re.compile(r's-background-color'))
        if category_badge:
            categories['primary'] = category_badge.get_text(strip=True)
        
        # Extract from title common categories
        title = self._extract_title(container)['full_title'].lower()
        common_categories = ['chair', 'sofa', 'table', 'bed', 'desk', 'cabinet', 'shelf']
        for category in common_categories:
            if category in title:
                categories['tags'].append(category)
        
        return categories
    
    def _extract_ad_info(self, container) -> Dict:
        """Extract advertising and sponsored content information."""
        ad_info = {
            'is_sponsored': False,
            'ad_type': '',
            'sponsor_info': {},
            'ad_position': ''
        }
        
        # Check for sponsored label
        sponsored_label = container.find('span', string=re.compile(r'Sponsored|Featured from Amazon'))
        if sponsored_label:
            ad_info['is_sponsored'] = True
            ad_info['ad_type'] = sponsored_label.get_text(strip=True)
        
        # Extract ad tracking data
        ad_tracking = container.find('div', {'data-component-type': 's-impression-logger'})
        if ad_tracking:
            ad_props = ad_tracking.get('data-component-props', '')
            if ad_props:
                try:
                    props_data = json.loads(html.unescape(ad_props))
                    ad_info['tracking_url'] = props_data.get('url', '')
                except json.JSONDecodeError:
                    pass
        
        return ad_info
    
    def _extract_badges(self, container) -> Dict:
        """Extract product badges and certifications."""
        badges = {
            'best_seller': False,
            'amazon_choice': False,
            'climate_pledge': False,
            'sustainability': [],
            'quality_badges': []
        }
        
        # Amazon's Choice badge
        choice_badge = container.find(string=re.compile(r"Amazon's Choice"))
        if choice_badge:
            badges['amazon_choice'] = True
        
        # Best seller badge
        bestseller = container.find(string=re.compile(r'Best Seller|#1 Best Seller'))
        if bestseller:
            badges['best_seller'] = True
        
        # Climate Pledge Friendly
        climate_badge = container.find('span', string=re.compile(r'Climate Pledge'))
        if climate_badge:
            badges['climate_pledge'] = True
        
        # Quality indicators
        quality_indicators = ['Top Reviewed', 'Highly rated', 'Premium quality']
        for indicator in quality_indicators:
            if container.find(string=re.compile(indicator, re.IGNORECASE)):
                badges['quality_badges'].append(indicator)
        
        return badges
    
    def _extract_product_metadata(self, container) -> Dict:
        """Extract additional product metadata."""
        metadata = {
            'position_in_results': '',
            'widget_id': '',
            'search_result_id': '',
            'has_variants': False,
            'prime_eligible': False,
            'fulfillment': {}
        }
        
        # Position in search results
        metadata['position_in_results'] = container.get('data-index', '')
        
        # Widget information
        widget = container.find('div', {'cel_widget_id': True})
        if widget:
            metadata['widget_id'] = widget.get('cel_widget_id', '')
        
        # Check if product has variants
        if self._extract_variants(container)['colors'] or self._extract_variants(container)['sizes']:
            metadata['has_variants'] = True
        
        # Prime eligibility
        free_shipping = self._extract_shipping_info(container)['free_shipping']
        metadata['prime_eligible'] = free_shipping
        
        return metadata
    
    def _generate_summary(self, products: List[Dict]) -> Dict:
        """Generate summary statistics for extracted products."""
        if not products:
            return {"error": "No products found"}
        
        total_products = len(products)
        sponsored_count = sum(1 for p in products if p.get('advertising', {}).get('is_sponsored', False))
        
        # Calculate average rating
        ratings = [p.get('reviews', {}).get('rating', {}).get('value', 0) for p in products if p.get('reviews', {}).get('rating', {}).get('value')]
        avg_rating = round(statistics.mean(ratings), 2) if ratings else 0
        
        # Price range
        prices = [p.get('pricing', {}).get('current_price', {}).get('amount', 0) for p in products if p.get('pricing', {}).get('current_price', {}).get('amount')]
        price_range = {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'avg': round(statistics.mean(prices), 2) if prices else 0
        }
        
        return {
            'total_products': total_products,
            'sponsored_products': sponsored_count,
            'organic_products': total_products - sponsored_count,
            'average_rating': avg_rating,
            'price_range': price_range,
            'products_with_reviews': sum(1 for p in products if p.get('reviews', {}).get('count', 0) > 0),
            'products_with_images': sum(1 for p in products if p.get('images', {}).get('primary', {}).get('url')),
            'free_shipping_count': sum(1 for p in products if p.get('shipping', {}).get('free_shipping', False))
        }
    
    def save_results(self, data: Dict, keyword: str) -> str:
        """Save extraction results to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_keyword = re.sub(r'[^\w\s-]', '', keyword).strip().replace(' ', '_')
        filename = f"amazon_realtime_{safe_keyword}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
            return ""
    
    def display_results_summary(self, data: Dict):
        """Display a formatted summary of extraction results."""
        summary = data.get('summary', {})
        metadata = data.get('metadata', {})
        
        print("\n" + "="*60)
        print("📊 REAL-TIME EXTRACTION SUMMARY")
        print("="*60)
        
        print(f"🔍 Search Keyword: {metadata.get('search_keyword', 'N/A')}")
        print(f"⏰ Extraction Time: {metadata.get('extraction_timestamp', 'N/A')}")
        print(f"📦 Total Products: {summary.get('total_products', 0)}")
        print(f"📺 Sponsored: {summary.get('sponsored_products', 0)}")
        print(f"🏢 Organic: {summary.get('organic_products', 0)}")
        print(f"⭐ Average Rating: {summary.get('average_rating', 0)}/5")
        
        price_range = summary.get('price_range', {})
        if price_range.get('max', 0) > 0:
            print(f"💰 Price Range: ${price_range.get('min', 0)} - ${price_range.get('max', 0)}")
            print(f"💵 Average Price: ${price_range.get('avg', 0)}")
        
        print(f"⭐ Products with Reviews: {summary.get('products_with_reviews', 0)}")
        print(f"🖼️ Products with Images: {summary.get('products_with_images', 0)}")
        print(f"🚚 Free Shipping: {summary.get('free_shipping_count', 0)}")
        
        # Show top 3 products
        products = data.get('products', [])[:3]
        if products:
            print(f"\n🏆 TOP 3 PRODUCTS:")
            for i, product in enumerate(products, 1):
                title = product.get('title', {}).get('short_title', 'N/A')
                price = product.get('pricing', {}).get('current_price', {}).get('amount', 'N/A')
                rating = product.get('reviews', {}).get('rating', {}).get('value', 'N/A')
                sponsored = "📺" if product.get('advertising', {}).get('is_sponsored', False) else "🏢"
                
                print(f"  {i}. {sponsored} {title}")
                print(f"     💰 ${price} | ⭐ {rating}/5")
        
        print("="*60)


def interactive_mode():
    """Run the extractor in interactive mode."""
    print("🚀 Amazon Real-Time Product Extractor")
    print("=" * 50)
    print("Enter keywords to search and extract Amazon product data in real-time!")
    print("Type 'quit' or 'exit' to stop.\n")
    
    # Initialize extractor
    extractor = RealTimeAmazonExtractor()
    
    while True:
        try:
            # Get user input
            keyword = input("🔍 Enter search keyword: ").strip()
            
            if keyword.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not keyword:
                print("⚠️ Please enter a valid keyword.")
                continue
            
            # Optional: Get number of pages
            try:
                pages_input = input("📄 Number of pages to scrape (default: 1): ").strip()
                max_pages = int(pages_input) if pages_input else 1
                max_pages = max(1, min(max_pages, 10))  # Limit to 1-10 pages
            except ValueError:
                max_pages = 1
            
            # Optional: Get delay
            try:
                delay_input = input("⏳ Delay between pages in seconds (default: 2): ").strip()
                delay = float(delay_input) if delay_input else 2.0
                delay = max(0.5, min(delay, 10.0))  # Limit to 0.5-10 seconds
            except ValueError:
                delay = 2.0
            
            print("\n" + "-"*50)
            
            # Extract data
            result = extractor.search_and_extract(keyword, max_pages, delay)
            
            # Display results
            extractor.display_results_summary(result)
            
            # Save results
            filename = extractor.save_results(result, keyword)
            
            print(f"\n💡 Results saved to: {filename}")
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Extraction interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            continue


def main():
    """Main function - can be used for both interactive and programmatic usage."""
    import sys
    
    if len(sys.argv) > 1:
        # Command line usage
        keyword = ' '.join(sys.argv[1:])
        extractor = RealTimeAmazonExtractor()
        result = extractor.search_and_extract(keyword)
        extractor.display_results_summary(result)
        extractor.save_results(result, keyword)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
