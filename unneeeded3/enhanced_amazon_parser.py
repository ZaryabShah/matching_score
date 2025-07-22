"""
Enhanced Amazon Product Parser with Advanced Matching Features
Designed for cross-platform product matching with comprehensive data extraction
"""

import re
import json
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import hashlib


class EnhancedAmazonProductParser:
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
            # Comprehensive specifications (all product details)
            "specifications": self._extract_comprehensive_specs(soup),
            
            # Matching identifiers
            "matching_data": self._extract_matching_identifiers(soup, basic_data),
            
            # Physical attributes extracted from specs
            "physical_attributes": self._extract_physical_attributes_from_specs(soup),
            
            # Performance attributes
            "performance_attributes": self._extract_performance_attributes(soup),
            
            # Compatibility information
            "compatibility": self._extract_compatibility_info(soup),
            
            # Materials and construction
            "materials": self._extract_materials_info(soup),
            
            # Package contents
            "package_contents": self._extract_package_contents(soup),
            
            # Certifications and standards
            "certifications": self._extract_certifications(soup),
            
            # Environmental attributes
            "environmental": self._extract_environmental_info(soup),
            
            # Usage context
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
            # Clean title for matching
            clean_title = re.sub(r'[^\w\s]', ' ', title.lower())
            clean_title = ' '.join(clean_title.split())
            identifiers['clean_title'] = clean_title
            
            # Extract key terms from title
            identifiers['title_keywords'] = self._extract_keywords_from_title(title)
        
        if brand:
            identifiers['brand_normalized'] = brand.lower().strip()
        
        return identifiers
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract meaningful keywords from product title"""
        # Common stop words to exclude
        stop_words = {
            'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'under', 'over'
        }
        
        # Clean and tokenize
        clean_title = re.sub(r'[^\w\s]', ' ', title.lower())
        words = clean_title.split()
        
        # Filter meaningful words
        keywords = []
        for word in words:
            if (len(word) > 2 and 
                word not in stop_words and 
                not word.isdigit() and
                not re.match(r'^\d+\w*$', word)):
                keywords.append(word)
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _extract_comprehensive_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive specifications from all product detail sections"""
        all_specs = {}
        
        # Primary product details table (the most important one)
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
        """Extract from the main product details table (productDetails_detailBullets_sections1)"""
        specs = {}
        
        # Main product details table
        table_selectors = [
            "#productDetails_detailBullets_sections1 tr",
            "#productDetails_detailBullets_sections2 tr",
            ".prodDetTable tr",
            "[id*='productDetails'] table tr"
        ]
        
        for selector in table_selectors:
            rows = soup.select(selector)
            for row in rows:
                # Look for th/td pairs or two td elements
                th_elem = row.select_one('th')
                td_elem = row.select_one('td')
                
                if th_elem and td_elem:
                    key = th_elem.get_text().strip()
                    value = td_elem.get_text().strip()
                    
                    # Clean up the value - remove extra whitespace and newlines
                    value = ' '.join(value.split())
                    
                    # Skip empty values or common non-useful entries
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
                
                # Handle rows with two td elements (alternative format)
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
        
        # Technical specifications section
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
        
        # Feature bullets that contain specifications
        bullet_elements = soup.select("#feature-bullets ul li span, .feature span")
        
        for bullet in bullet_elements:
            text = bullet.get_text().strip()
            
            # Look for key:value patterns in bullets
            if ':' in text and len(text) < 200:  # Reasonable length for specs
                parts = text.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Clean HTML tags and extra whitespace
                    value = ' '.join(value.split())
                    
                    if value and key and not self._is_skip_entry(key, value):
                        specs[key] = value
        
        return specs
    
    def _extract_additional_info_tables(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract from additional information tables"""
        specs = {}
        
        # Additional tables that might contain specs
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
        # Skip entries that are not useful for product matching
        skip_patterns = [
            # Empty or too short
            len(value.strip()) < 2,
            # Common non-spec entries
            'see top 100' in value.lower(),
            'click here' in value.lower(),
            'javascript:' in value.lower(),
            'out of 5 stars' in value.lower(),
            # Keys that are not specifications
            key.lower() in ['customer reviews', 'best sellers rank', 'feedback'],
            # HTML artifacts
            value.startswith('data:'),
            'href=' in value,
            '<' in value and '>' in value
        ]
        
        return any(skip_patterns)
    
    def _categorize_specification(self, key: str) -> str:
        """Categorize specification based on key"""
        key_lower = key.lower()
        
        dimension_keys = ['dimension', 'size', 'width', 'height', 'length', 'depth', 'weight', 'capacity']
        material_keys = ['material', 'fabric', 'construction', 'finish', 'color', 'style']
        electrical_keys = ['voltage', 'wattage', 'power', 'battery', 'amperage', 'frequency']
        performance_keys = ['speed', 'efficiency', 'rating', 'performance', 'capacity', 'output']
        
        if any(dim_key in key_lower for dim_key in dimension_keys):
            return "dimensions"
        elif any(mat_key in key_lower for mat_key in material_keys):
            return "materials"
        elif any(elec_key in key_lower for elec_key in electrical_keys):
            return "electrical"
        elif any(perf_key in key_lower for perf_key in performance_keys):
            return "performance"
        else:
            return "technical"
    
    def _extract_physical_attributes_from_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract physical attributes from comprehensive specifications"""
        attributes = {}
        
        # First get comprehensive specs
        specs = self._extract_comprehensive_specs(soup)
        
        # Extract dimensions from specs
        dimension_keys = [
            'Product Dimensions', 'Dimensions', 'Size', 'Item Dimensions',
            'Package Dimensions', 'Overall Dimensions'
        ]
        
        for key in dimension_keys:
            if key in specs:
                dim_text = specs[key]
                # Parse dimension patterns like "19.7"D x 18.9"W x 38"H"
                patterns = [
                    r'(\d+\.?\d*)"?D\s*x\s*(\d+\.?\d*)"?W\s*x\s*(\d+\.?\d*)"?H',
                    r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inches',
                    r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, dim_text, re.IGNORECASE)
                    if match:
                        attributes['dimensions'] = {
                            'depth': float(match.group(1)),
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
        
        # Extract finish
        finish_keys = ['Finish Type', 'Finish', 'Furniture Finish']
        for key in finish_keys:
            if key in specs:
                attributes['finish'] = specs[key]
                break
        
        # Extract specific measurements
        measurement_keys = {
            'seat_height': ['Seat Height', 'Chair Height'],
            'seat_depth': ['Seat Depth'],
            'seat_length': ['Seat Length', 'Seat Width'],
            'backrest_height': ['Seat Back Interior Height', 'Back Height'],
            'backrest_width': ['Chair Backrest Width', 'Back Width'],
            'arm_style': ['Arm Style'],
            'leg_style': ['Leg Style']
        }
        
        for attr_name, possible_keys in measurement_keys.items():
            for key in possible_keys:
                if key in specs:
                    value = specs[key]
                    # Extract numeric values for measurements
                    if any(word in attr_name for word in ['height', 'depth', 'length', 'width']):
                        num_match = re.search(r'(\d+\.?\d*)\s*(inches?|in|cm)', value, re.IGNORECASE)
                        if num_match:
                            attributes[attr_name] = {
                                'value': float(num_match.group(1)),
                                'unit': num_match.group(2).lower(),
                                'original_text': value
                            }
                        else:
                            attributes[attr_name] = value
                    else:
                        attributes[attr_name] = value
                    break
        
        return attributes
    
    def _extract_physical_attributes(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed physical attributes (legacy method, now calls enhanced version)"""
        return self._extract_physical_attributes_from_specs(soup)
    
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
        
        # Capacity/Volume
        capacity_patterns = [
            r'Capacity:?\s*(\d+\.?\d*)\s*(liters?|gallons?|quarts?|oz|ml)',
            r'Volume:?\s*(\d+\.?\d*)\s*(liters?|gallons?|quarts?|oz|ml)',
            r'(\d+\.?\d*)\s*(cup|cups|liter|liters|gallon|gallons)'
        ]
        
        for pattern in capacity_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                attributes['capacity'] = {
                    'value': float(match.group(1)),
                    'unit': match.group(2).lower()
                }
                break
        
        return attributes
    
    def _extract_compatibility_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract compatibility information"""
        compatibility = {}
        page_text = soup.get_text()
        
        # Compatible devices/systems
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
        
        # Look for package contents sections
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
        
        # Extract from title and description
        title = self._extract_title(soup) or ""
        desc = self._extract_description(soup) or ""
        
        # Room/location context
        room_keywords = ['living room', 'bedroom', 'kitchen', 'bathroom', 'office', 'outdoor', 'garage', 'basement']
        rooms = [room for room in room_keywords if room.lower() in (title + " " + desc).lower()]
        if rooms:
            context['rooms'] = rooms
        
        # Use case context
        use_keywords = ['gaming', 'work', 'exercise', 'cooking', 'cleaning', 'storage', 'decoration']
        uses = [use for use in use_keywords if use.lower() in (title + " " + desc).lower()]
        if uses:
            context['use_cases'] = uses
        
        return context
    
    def _generate_product_fingerprint(self, product_data: Dict[str, Any]) -> str:
        """Generate a fingerprint for product matching"""
        # Combine key identifying features
        fingerprint_data = {
            'brand': product_data.get('brand', '').lower(),
            'clean_title': product_data.get('matching_data', {}).get('clean_title', ''),
            'model_number': product_data.get('matching_data', {}).get('model_number', ''),
            'dimensions': product_data.get('physical_attributes', {}).get('dimensions', {}),
            'weight': product_data.get('physical_attributes', {}).get('weight', {})
        }
        
        # Create hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    # Include all the basic extraction methods from the original parser
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
        
        list_price_elem = soup.select_one(".a-price.a-text-price .a-offscreen")
        if list_price_elem:
            pricing['list_price'] = list_price_elem.get_text().strip()
        
        savings_elem = soup.select_one(".savingsPercentage")
        if savings_elem:
            pricing['savings'] = savings_elem.get_text().strip()
        
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


# Convenience functions
def parse_amazon_product_enhanced(html_file_path: str, source_url: str = None) -> Dict[str, Any]:
    """Parse Amazon product with enhanced matching features"""
    parser = EnhancedAmazonProductParser()
    
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    return parser.parse(html_content, source_url)


def compare_products(product1: Dict[str, Any], product2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two products for similarity"""
    comparison = {
        'fingerprint_match': product1.get('fingerprint') == product2.get('fingerprint'),
        'brand_match': (product1.get('brand', '').lower() == product2.get('brand', '').lower()),
        'title_similarity': 0.0,
        'spec_overlap': 0.0,
        'dimension_match': False,
        'model_match': False
    }
    
    # Title similarity (simple word overlap)
    title1_words = set(product1.get('matching_data', {}).get('title_keywords', []))
    title2_words = set(product2.get('matching_data', {}).get('title_keywords', []))
    
    if title1_words and title2_words:
        overlap = len(title1_words.intersection(title2_words))
        union = len(title1_words.union(title2_words))
        comparison['title_similarity'] = overlap / union if union > 0 else 0.0
    
    # Model number match
    model1 = product1.get('matching_data', {}).get('model_number')
    model2 = product2.get('matching_data', {}).get('model_number')
    comparison['model_match'] = model1 and model2 and model1.lower() == model2.lower()
    
    # Dimension comparison
    dim1 = product1.get('physical_attributes', {}).get('dimensions')
    dim2 = product2.get('physical_attributes', {}).get('dimensions')
    if dim1 and dim2:
        # Allow 5% tolerance for dimension matching
        tolerance = 0.05
        matches = []
        for key in ['length', 'width', 'height']:
            if key in dim1 and key in dim2:
                val1, val2 = float(dim1[key]), float(dim2[key])
                diff = abs(val1 - val2) / max(val1, val2) if max(val1, val2) > 0 else 0
                matches.append(diff <= tolerance)
        comparison['dimension_match'] = all(matches) if matches else False
    
    return comparison


if __name__ == "__main__":
    # Test the enhanced parser
    html_files = [
        "amazon_response.html",
        "amazon_response1.html"
    ]
    
    parsed_products = []
    
    for html_file in html_files:
        try:
            print(f"Enhanced parsing {html_file}...")
            parsed_data = parse_amazon_product_enhanced(html_file)
            
            output_file = f"enhanced_parsed_{html_file.replace('.html', '.json')}"
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(parsed_data, file, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully parsed and saved to {output_file}")
            print(f"   ASIN: {parsed_data.get('asin', 'N/A')}")
            print(f"   Title: {parsed_data.get('title', 'N/A')[:80]}...")
            print(f"   Brand: {parsed_data.get('brand', 'N/A')}")
            print(f"   Model: {parsed_data.get('matching_data', {}).get('model_number', 'N/A')}")
            print(f"   Fingerprint: {parsed_data.get('fingerprint', 'N/A')[:16]}...")
            print(f"   Keywords: {parsed_data.get('matching_data', {}).get('title_keywords', [])[:5]}")
            print()
            
            parsed_products.append(parsed_data)
            
        except Exception as e:
            print(f"❌ Error parsing {html_file}: {str(e)}")
    
    # Compare products if we have two
    if len(parsed_products) == 2:
        print("🔍 Comparing products...")
        comparison = compare_products(parsed_products[0], parsed_products[1])
        
        with open("product_comparison.json", 'w', encoding='utf-8') as file:
            json.dump(comparison, file, indent=2)
        
        print(f"Brand Match: {comparison['brand_match']}")
        print(f"Title Similarity: {comparison['title_similarity']:.2%}")
        print(f"Model Match: {comparison['model_match']}")
        print(f"Dimension Match: {comparison['dimension_match']}")
        print(f"Fingerprint Match: {comparison['fingerprint_match']}")
