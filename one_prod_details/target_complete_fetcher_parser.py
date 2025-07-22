#!/usr/bin/env python3
"""
Complete Target Product Fetcher and Parser
Fetches product pages from Target.com and extracts comprehensive product data
Usage: python target_complete_fetcher_parser.py <target_url>
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


class TargetProductFetcher:
    """
    Fetches Target product pages with proper headers and error handling.
    """
    
    def __init__(self, use_session=True):
        self.session = requests.Session() if use_session else None
        self.setup_headers()
    
    def setup_headers(self):
        """Setup realistic browser headers for Target.com requests."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    
    def fetch_product(self, url: str, save_html: bool = False) -> str:
        """
        Fetch Target product page HTML.
        
        Args:
            url: Target product URL
            save_html: Whether to save HTML to file for debugging
            
        Returns:
            HTML content of the product page
        """
        try:
            # Validate URL
            if not self._is_valid_target_url(url):
                raise ValueError(f"Invalid Target URL: {url}")
            
            print(f"🌐 Fetching product from: {url}")
            
            # Add random delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            # Make the request
            if self.session:
                response = self.session.get(url, headers=self.headers, timeout=30)
            else:
                response = requests.get(url, headers=self.headers, timeout=30)
            
            response.raise_for_status()
            
            print(f"✅ Successfully fetched page (Status: {response.status_code})")
            print(f"📊 Content size: {len(response.text):,} characters")
            
            # Save HTML if requested
            if save_html:
                filename = f"target_product_{int(time.time())}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 Saved HTML to: {filename}")
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch product page: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching product: {str(e)}")
    
    def _is_valid_target_url(self, url: str) -> bool:
        """Validate if URL is a Target product URL."""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc.lower() in ['www.target.com', 'target.com'] and
                '/p/' in parsed.path.lower()
            )
        except:
            return False


class TargetProductParser:
    """
    Enhanced Target product parser for comprehensive product specification extraction.
    Provides detailed product information extraction for cross-platform matching.
    """
    
    def __init__(self):
        self.extracted_data = {}
        self.raw_json_data = {}
        
    def parse_html(self, html_content: str) -> Dict[str, Any]:
        """
        Parse Target product page HTML and extract comprehensive product data.
        
        Args:
            html_content: Raw HTML content from Target product page
            
        Returns:
            Dictionary containing comprehensive product specifications
        """
        try:
            # Extract data from multiple sources
            target_data = None
            
            # Try __TGT_DATA__ first (main product data source)
            target_data = self._extract_tgt_data(html_content)
            
            # If not found, try __NEXT_DATA__
            if not target_data:
                target_data = self._extract_next_data(html_content)
            
            if not target_data:
                return {"error": "Failed to extract product data from HTML"}
                
            # Store raw data for debugging
            self.raw_json_data = target_data
            
            # Extract comprehensive product specifications
            product_specs = self._extract_comprehensive_specs(target_data)
            
            # Store extracted data
            self.extracted_data = product_specs
            
            return product_specs
            
        except Exception as e:
            return {"error": f"Parsing failed: {str(e)}"}
    
    def _extract_tgt_data(self, html_content: str) -> Optional[Dict]:
        """Extract and parse the __TGT_DATA__ JSON from Target page."""
        try:
            # Find the __TGT_DATA__ object
            pattern = r"'__TGT_DATA__':\s*{\s*configurable:\s*false,\s*enumerable:\s*true,\s*value:\s*deepFreeze\(JSON\.parse\(\"(.*?)\"\)\)"
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                return None
                
            json_string = match.group(1)
            # Unescape the JSON string
            json_string = json_string.replace('\\"', '"').replace('\\\\', '\\')
            
            return json.loads(json_string)
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error extracting __TGT_DATA__: {e}")
            return None
    
    def _extract_next_data(self, html_content: str) -> Optional[Dict]:
        """Extract and parse the __NEXT_DATA__ JSON from Target page."""
        try:
            # Find the __NEXT_DATA__ script tag
            pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                return None
                
            json_content = match.group(1)
            return json.loads(json_content)
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error extracting __NEXT_DATA__: {e}")
            return None
    
    def _extract_comprehensive_specs(self, data: Dict) -> Dict[str, Any]:
        """Extract comprehensive product specifications from extracted data."""
        specs = {
            "basic_info": {},
            "pricing": {},
            "physical_attributes": {},
            "product_details": {},
            "images": {},
            "vendor_info": {},
            "category_info": {},
            "reviews": {},
            "fulfillment": {},
            "variations": {},
            "enrichment_data": {},
            "technical_specs": {},
            "compatibility": {},
            "raw_data_sources": []
        }
        
        try:
            # Check if this is TGT_DATA format with __PRELOADED_QUERIES__
            if "__PRELOADED_QUERIES__" in data:
                queries = data["__PRELOADED_QUERIES__"].get("queries", [])
                
                for query in queries:
                    if len(query) >= 2 and isinstance(query[1], dict):
                        query_data = query[1]
                        
                        # Extract product data from PDP query
                        if "data" in query_data and isinstance(query_data["data"], dict):
                            if "product" in query_data["data"]:
                                self._extract_from_pdp_data(query_data["data"]["product"], specs)
                            
                            # Extract from content data
                            if "metadata" in query_data["data"]:
                                self._extract_from_content_data(query_data["data"], specs)
            
            # Check if this is NEXT_DATA format
            elif "props" in data:
                # Extract from preloaded queries if available
                page_props = data.get("props", {}).get("pageProps", {})
                if "__PRELOADED_QUERIES__" in page_props:
                    queries = page_props["__PRELOADED_QUERIES__"].get("queries", [])
                    
                    for query in queries:
                        if len(query) >= 2 and isinstance(query[1], dict):
                            query_data = query[1]
                            
                            # Extract product data from PDP query
                            if "data" in query_data and "product" in query_data.get("data", {}):
                                self._extract_from_pdp_data(query_data["data"]["product"], specs)
                            
                            # Extract from content data
                            if "data" in query_data and "metadata" in query_data.get("data", {}):
                                self._extract_from_content_data(query_data["data"], specs)
                
                # Extract from page content if available
                if page_props:
                    self._extract_from_page_props(page_props, specs)
            
            # Clean and standardize data
            self._standardize_specifications(specs)
            
            return specs
            
        except Exception as e:
            specs["extraction_error"] = str(e)
            return specs
    
    def _extract_from_pdp_data(self, product_data: Dict, specs: Dict):
        """Extract data from PDP (Product Detail Page) data structure."""
        try:
            # Basic product information
            specs["basic_info"].update({
                "tcin": product_data.get("tcin"),
                "name": product_data.get("item", {}).get("product_description", {}).get("title", ""),
                "short_description": product_data.get("item", {}).get("product_description", {}).get("downstream_description", ""),
                "brand": product_data.get("item", {}).get("primary_brand", {}).get("name"),
                "brand_url": product_data.get("item", {}).get("primary_brand", {}).get("canonical_url"),
                "model_number": product_data.get("tcin"),  # TCIN serves as model
                "manufacturer": product_data.get("item", {}).get("primary_brand", {}).get("name"),
            })
            
            # Pricing information
            price_info = product_data.get("price", {})
            specs["pricing"].update({
                "current_price": price_info.get("current_retail"),
                "regular_price": price_info.get("reg_retail"),
                "formatted_current_price": price_info.get("formatted_current_price"),
                "formatted_regular_price": price_info.get("formatted_comparison_price"),
                "price_type": price_info.get("formatted_current_price_type"),
                "comparison_price_type": price_info.get("formatted_comparison_price_type"),
                "save_amount": price_info.get("save_dollar"),
                "save_percentage": price_info.get("save_percent"),
                "location_id": price_info.get("location_id"),
            })
            
            # Physical attributes and dimensions
            package_dims = product_data.get("item", {}).get("package_dimensions", {})
            specs["physical_attributes"].update({
                "weight": package_dims.get("weight"),
                "weight_unit": package_dims.get("weight_unit_of_measure"),
                "length": package_dims.get("depth"),  # Target uses depth for length
                "width": package_dims.get("width"),
                "height": package_dims.get("height"),
                "dimension_unit": package_dims.get("dimension_unit_of_measure"),
            })
            
            # Extract detailed specifications from bullet points
            self._extract_bullet_specifications(product_data.get("item", {}), specs)
            
            # Images
            self._extract_image_data(product_data.get("item", {}), specs)
            
            # Vendor information
            vendors = product_data.get("item", {}).get("product_description", {}).get("product_vendors", [])
            if vendors:
                vendor = vendors[0]
                specs["vendor_info"].update({
                    "vendor_name": vendor.get("vendor_name"),
                    "vendor_id": vendor.get("id"),
                    "vendor_uri": vendor.get("uri"),
                })
            
            # Category information
            category = product_data.get("category", {})
            specs["category_info"].update({
                "category_name": category.get("name"),
                "parent_category_id": category.get("parent_category_id"),
                "breadcrumbs": category.get("breadcrumbs", [])
            })
            
            # Reviews and ratings
            reviews = product_data.get("ratings_and_reviews", {})
            stats = reviews.get("statistics", {})
            rating_info = stats.get("rating", {})
            specs["reviews"].update({
                "average_rating": rating_info.get("average"),
                "total_reviews": rating_info.get("count"),
                "rating_distribution": rating_info.get("distribution", {}),
                "secondary_ratings": rating_info.get("secondary_averages", []),
                "recommended_count": stats.get("recommended_count"),
                "not_recommended_count": stats.get("not_recommended_count"),
                "recommended_percentage": stats.get("recommended_percentage"),
                "question_count": stats.get("question_count"),
                "has_verified_reviews": reviews.get("has_verified"),
                "recent_reviews": reviews.get("most_recent", []),
                "review_photos": reviews.get("photos", [])
            })
            
            # Fulfillment information
            fulfillment = product_data.get("item", {}).get("fulfillment", {})
            specs["fulfillment"].update({
                "is_marketplace": fulfillment.get("is_marketplace"),
                "purchase_limit": fulfillment.get("purchase_limit"),
                "po_box_prohibited": fulfillment.get("po_box_prohibited_message"),
                "shipping_exclusions": fulfillment.get("shipping_exclusion_codes", []),
                "return_method": product_data.get("item", {}).get("return_method"),
                "return_policies": product_data.get("item", {}).get("enrichment", {}).get("return_policies", [])
            })
            
            # Product variations
            variations = product_data.get("variation_hierarchy", [])
            specs["variations"]["color_variations"] = []
            for var in variations:
                if var.get("name") == "color":
                    specs["variations"]["color_variations"].append({
                        "color": var.get("value"),
                        "tcin": var.get("tcin"),
                        "swatch_image": var.get("swatch_image_url"),
                        "primary_image": var.get("primary_image_url")
                    })
            
            # Child products (color variations)
            children = product_data.get("children", [])
            specs["variations"]["child_products"] = []
            for child in children:
                if child.get("item"):
                    child_info = {
                        "tcin": child.get("tcin"),
                        "primary_barcode": child.get("item", {}).get("primary_barcode"),
                        "price": child.get("price", {}),
                        "esp_protection": child.get("esp", {})
                    }
                    specs["variations"]["child_products"].append(child_info)
        
        except Exception as e:
            specs["pdp_extraction_error"] = str(e)
    
    def _extract_bullet_specifications(self, item_data: Dict, specs: Dict):
        """Extract detailed specifications from bullet descriptions."""
        try:
            bullets = item_data.get("product_description", {}).get("bullet_descriptions", [])
            
            # Initialize categories
            specs["technical_specs"]["specifications"] = {}
            specs["physical_attributes"]["detailed_dimensions"] = {}
            specs["product_details"]["features"] = []
            specs["product_details"]["materials"] = []
            specs["product_details"]["care_instructions"] = []
            
            for bullet in bullets:
                # Remove HTML tags
                clean_bullet = re.sub(r'<[^>]+>', '', bullet)
                
                # Parse key-value pairs
                if ':' in clean_bullet:
                    key, value = clean_bullet.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Categorize specifications
                    if any(dim_word in key.lower() for dim_word in ['dimension', 'width', 'height', 'depth', 'weight', 'size']):
                        specs["physical_attributes"]["detailed_dimensions"][key] = value
                    elif any(material_word in key.lower() for material_word in ['material', 'fabric', 'construction']):
                        specs["product_details"]["materials"].append(f"{key}: {value}")
                    elif any(care_word in key.lower() for care_word in ['care', 'cleaning', 'maintenance', 'wash']):
                        specs["product_details"]["care_instructions"].append(f"{key}: {value}")
                    else:
                        specs["technical_specs"]["specifications"][key] = value
                else:
                    # Add as general feature
                    specs["product_details"]["features"].append(clean_bullet)
            
            # Extract soft bullets (highlights)
            soft_bullets = item_data.get("product_description", {}).get("soft_bullets", {}).get("bullets", [])
            specs["product_details"]["highlights"] = soft_bullets
            
            # Extract classification info
            classification = item_data.get("product_classification", {})
            specs["product_details"].update({
                "product_type": classification.get("product_type_name"),
                "product_type_id": classification.get("product_type"),
                "purchase_behavior": classification.get("purchase_behavior")
            })
            
            # Extract merchandise classification
            merch_class = item_data.get("merchandise_classification", {})
            specs["category_info"].update({
                "department_name": merch_class.get("department_name"),
                "department_id": merch_class.get("department_id"),
                "class_id": merch_class.get("class_id")
            })
            
            # Extract handling information
            handling = item_data.get("handling", {})
            specs["product_details"]["import_designation"] = handling.get("import_designation_description")
            
            # Extract warranty information
            warranty_bullet = next((b for b in bullets if 'warranty' in b.lower()), None)
            if warranty_bullet:
                specs["product_details"]["warranty"] = re.sub(r'<[^>]+>', '', warranty_bullet)
        
        except Exception as e:
            specs["bullet_extraction_error"] = str(e)
    
    def _extract_image_data(self, item_data: Dict, specs: Dict):
        """Extract comprehensive image information."""
        try:
            # Get image info from enrichment data
            image_info = item_data.get("enrichment", {}).get("image_info", {})
            images = item_data.get("enrichment", {}).get("images", {})
            
            specs["images"].update({
                "base_url": image_info.get("base_url") or images.get("base_url"),
                "primary_image": {
                    "url": image_info.get("primary_image", {}).get("url") or images.get("primary_image_url"),
                    "name": image_info.get("primary_image", {}).get("image_name") or images.get("primary_image")
                },
                "swatch_image": {
                    "url": image_info.get("swatch_image", {}).get("url") or images.get("swatch_image_url"),
                    "name": image_info.get("swatch_image", {}).get("image_name") or images.get("swatch_image")
                },
                "alternate_images": [],
                "content_labels": image_info.get("content_labels", [])
            })
            
            # Process alternate images
            alt_images = image_info.get("alternate_images", []) or images.get("alternate_image_urls", [])
            for img in alt_images:
                if isinstance(img, dict):
                    specs["images"]["alternate_images"].append({
                        "url": img.get("url"),
                        "name": img.get("image_name")
                    })
                else:
                    specs["images"]["alternate_images"].append({"url": img, "name": ""})
        
        except Exception as e:
            specs["image_extraction_error"] = str(e)
    
    def _extract_from_content_data(self, content_data: Dict, specs: Dict):
        """Extract data from content/page data structure."""
        try:
            metadata = content_data.get("metadata", {})
            
            # SEO and metadata
            seo_data = metadata.get("seo", {})
            specs["enrichment_data"].update({
                "canonical_url": seo_data.get("canonical_url"),
                "seo_title": seo_data.get("seo_title"),
                "seo_description": seo_data.get("seo_description"),
                "seo_keywords": seo_data.get("seo_keywords"),
                "page_type": seo_data.get("page_type"),
                "activation_date": metadata.get("activation_date")
            })
            
            # OpenGraph data
            og_data = metadata.get("og", {})
            specs["enrichment_data"]["open_graph"] = og_data
            
            # Twitter card data
            twitter_data = metadata.get("twitter", {})
            specs["enrichment_data"]["twitter_card"] = twitter_data
        
        except Exception as e:
            specs["content_extraction_error"] = str(e)
    
    def _extract_from_page_props(self, page_props: Dict, specs: Dict):
        """Extract additional data from page props."""
        try:
            # Add any additional page-level data
            if "isProductDetailServerSideRenderPriceEnabled" in page_props:
                specs["enrichment_data"]["ssr_price_enabled"] = page_props["isProductDetailServerSideRenderPriceEnabled"]
        
        except Exception as e:
            specs["page_props_extraction_error"] = str(e)
    
    def _standardize_specifications(self, specs: Dict):
        """Clean and standardize extracted specifications."""
        try:
            # Clean up empty values
            for category in specs:
                if isinstance(specs[category], dict):
                    specs[category] = {k: v for k, v in specs[category].items() if v not in [None, "", [], {}]}
            
            # Standardize UPC/GTIN from barcode
            for child in specs.get("variations", {}).get("child_products", []):
                if "primary_barcode" in child:
                    specs["basic_info"]["upc"] = child["primary_barcode"]
                    specs["basic_info"]["gtin"] = child["primary_barcode"]
                    break
            
            # Extract ASIN equivalent (TCIN)
            if specs["basic_info"].get("tcin"):
                specs["basic_info"]["asin_equivalent"] = specs["basic_info"]["tcin"]
            
            # Standardize dimensions
            phys_attrs = specs["physical_attributes"]
            if all(k in phys_attrs for k in ["length", "width", "height"]):
                specs["physical_attributes"]["dimensions_combined"] = f"{phys_attrs['length']} x {phys_attrs['width']} x {phys_attrs['height']} {phys_attrs.get('dimension_unit', '')}"
            
            # Calculate total feature count
            feature_count = 0
            feature_count += len(specs.get("product_details", {}).get("features", []))
            feature_count += len(specs.get("product_details", {}).get("highlights", []))
            feature_count += len(specs.get("technical_specs", {}).get("specifications", {}))
            specs["basic_info"]["total_specifications"] = feature_count
            
            # Add extraction timestamp
            specs["basic_info"]["extraction_timestamp"] = datetime.now().isoformat()
            
        except Exception as e:
            specs["standardization_error"] = str(e)
    
    def get_comparison_data(self) -> Dict[str, Any]:
        """
        Get standardized data for cross-platform product comparison.
        Returns key fields in a consistent format for matching with other platforms.
        """
        if not self.extracted_data:
            return {}
        
        basic = self.extracted_data.get("basic_info", {})
        pricing = self.extracted_data.get("pricing", {})
        physical = self.extracted_data.get("physical_attributes", {})
        details = self.extracted_data.get("product_details", {})
        
        return {
            "platform": "Target",
            "product_id": basic.get("tcin"),
            "name": basic.get("name"),
            "brand": basic.get("brand"),
            "model": basic.get("model_number"),
            "upc": basic.get("upc"),
            "gtin": basic.get("gtin"),
            "current_price": pricing.get("current_price"),
            "regular_price": pricing.get("regular_price"),
            "dimensions": {
                "length": physical.get("length"),
                "width": physical.get("width"),
                "height": physical.get("height"),
                "weight": physical.get("weight"),
                "unit": physical.get("dimension_unit")
            },
            "features": details.get("features", []) + details.get("highlights", []),
            "materials": details.get("materials", []),
            "specifications": self.extracted_data.get("technical_specs", {}).get("specifications", {}),
            "total_specs": basic.get("total_specifications", 0),
            "extraction_source": "target_complete_fetcher_parser.py"
        }


class TargetProductExtractor:
    """
    Complete Target product extraction system that combines fetching and parsing.
    """
    
    def __init__(self, save_html: bool = False, save_json: bool = True):
        self.fetcher = TargetProductFetcher()
        self.parser = TargetProductParser()
        self.save_html = save_html
        self.save_json = save_json
    
    def extract_product(self, url: str) -> Dict[str, Any]:
        """
        Complete product extraction from Target URL.
        
        Args:
            url: Target product URL
            
        Returns:
            Complete product specifications dictionary
        """
        try:
            print(f"🎯 Starting Target product extraction...")
            print(f"📋 URL: {url}")
            print(f"⚙️  Settings: Save HTML={self.save_html}, Save JSON={self.save_json}")
            print("-" * 60)
            
            # Step 1: Fetch the product page
            html_content = self.fetcher.fetch_product(url, save_html=self.save_html)
            
            # Step 2: Parse the HTML content
            print(f"\n🔍 Parsing product data...")
            product_data = self.parser.parse_html(html_content)
            
            if "error" in product_data:
                print(f"❌ Parsing failed: {product_data['error']}")
                return product_data
            
            # Step 3: Save JSON if requested
            if self.save_json:
                timestamp = int(time.time())
                tcin = product_data.get("basic_info", {}).get("tcin", "unknown")
                filename = f"target_product_{tcin}_{timestamp}.json"
                
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
        print(f"🎯 TARGET PRODUCT EXTRACTION COMPLETE")
        print(f"=" * 60)
        
        basic_info = product_data.get("basic_info", {})
        pricing = product_data.get("pricing", {})
        physical = product_data.get("physical_attributes", {})
        reviews = product_data.get("reviews", {})
        
        print(f"📦 Product: {basic_info.get('name', 'N/A')}")
        print(f"🏷️  Brand: {basic_info.get('brand', 'N/A')}")
        print(f"🆔 TCIN: {basic_info.get('tcin', 'N/A')}")
        print(f"🔢 UPC: {basic_info.get('upc', 'N/A')}")
        print(f"💰 Price: {pricing.get('formatted_current_price', 'N/A')}")
        if pricing.get('formatted_regular_price'):
            print(f"   Regular: {pricing.get('formatted_regular_price', 'N/A')}")
            if pricing.get('save_amount'):
                print(f"   Savings: ${pricing.get('save_amount', 0)} ({pricing.get('save_percentage', 0)}% off)")
        
        print(f"📏 Dimensions: {physical.get('dimensions_combined', 'N/A')}")
        print(f"⚖️  Weight: {physical.get('weight', 'N/A')} {physical.get('weight_unit', '')}")
        print(f"⭐ Rating: {reviews.get('average_rating', 'N/A')} ({reviews.get('total_reviews', 0)} reviews)")
        print(f"📊 Total Specifications: {basic_info.get('total_specifications', 0)}")
        
        # Show top specifications
        tech_specs = product_data.get("technical_specs", {}).get("specifications", {})
        if tech_specs:
            print(f"\n🔧 Key Specifications:")
            for key, value in list(tech_specs.items())[:5]:
                print(f"   • {key}: {value}")
            if len(tech_specs) > 5:
                print(f"   ... and {len(tech_specs) - 5} more")
        
        # Show top features
        features = product_data.get("product_details", {}).get("features", [])
        highlights = product_data.get("product_details", {}).get("highlights", [])
        all_features = features + highlights
        
        if all_features:
            print(f"\n✨ Key Features:")
            for feature in all_features[:3]:
                print(f"   • {feature[:80]}{'...' if len(feature) > 80 else ''}")
            if len(all_features) > 3:
                print(f"   ... and {len(all_features) - 3} more features")
        
        # Show variations
        variations = product_data.get("variations", {}).get("color_variations", [])
        if variations:
            print(f"\n🎨 Available Colors: {len(variations)} options")
            for var in variations[:3]:
                print(f"   • {var.get('color', 'N/A')}")
            if len(variations) > 3:
                print(f"   ... and {len(variations) - 3} more colors")
        
        print(f"\n✅ Extraction completed successfully!")
        print(f"🕐 Timestamp: {basic_info.get('extraction_timestamp', 'N/A')}")
        print(f"=" * 60)


def main():
    """Main function for command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python target_complete_fetcher_parser.py <target_url>")
        print("Example: python target_complete_fetcher_parser.py 'https://www.target.com/p/product-name/-/A-12345678'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Create extractor with default settings
    extractor = TargetProductExtractor(save_html=True, save_json=True)
    
    # Extract product
    result = extractor.extract_product(url)
    
    if "error" in result:
        sys.exit(1)
    
    print(f"\n🎉 Product extraction completed successfully!")


def demo_with_example():
    """Demo function with example URL."""
    example_url = "https://www.target.com/p/wicker-egg-chair-with-ottoman-egg-basket-lounge-chair-with-thick-cushion-comfy-egg-rattan-seat-for-indoor-outdoor-patio-porch-backyard/-/A-1001689724"
    
    print("🎯 Target Product Fetcher & Parser Demo")
    print("=" * 50)
    
    extractor = TargetProductExtractor(save_html=True, save_json=True)
    result = extractor.extract_product(example_url)
    
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
        # Run with provided URL
        main()
