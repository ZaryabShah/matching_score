#!/usr/bin/env python3
"""
Enhanced Target Product Parser
Comprehensive product specification extraction for Target.com products
Matches Amazon parser capabilities for cross-platform product matching
"""

import json
import re
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import copy

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
                    specs["images"]["alternate_images"].append({
                        "url": img,
                        "name": img.split('/')[-1] if '/' in str(img) else str(img)
                    })
        
        except Exception as e:
            specs["image_extraction_error"] = str(e)
    
    def _extract_from_content_data(self, content_data: Dict, specs: Dict):
        """Extract data from content/page data structure."""
        try:
            metadata = content_data.get("metadata", {})
            if metadata:
                seo_data = metadata.get("seo_data", {})
                specs["basic_info"].update({
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
            from datetime import datetime
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
            "extraction_source": "target_product_parser.py"
        }
    
    def compare_with_other_product(self, other_product_data: Dict) -> Dict[str, Any]:
        """
        Compare this Target product with data from another platform.
        
        Args:
            other_product_data: Product data from another platform parser
            
        Returns:
            Comparison analysis with similarity scores and matching fields
        """
        target_data = self.get_comparison_data()
        
        if not target_data or not other_product_data:
            return {"error": "Missing product data for comparison"}
        
        comparison = {
            "target_product": target_data.get("name", "Unknown"),
            "other_product": other_product_data.get("name", "Unknown"),
            "target_platform": "Target",
            "other_platform": other_product_data.get("platform", "Unknown"),
            "matches": {},
            "differences": {},
            "similarity_score": 0.0,
            "match_confidence": "Low"
        }
        
        # Compare key fields
        key_fields = ["name", "brand", "model", "upc", "gtin"]
        matches = 0
        total_fields = 0
        
        for field in key_fields:
            target_val = target_data.get(field)
            other_val = other_product_data.get(field)
            
            if target_val and other_val:
                total_fields += 1
                if str(target_val).lower() == str(other_val).lower():
                    matches += 1
                    comparison["matches"][field] = {
                        "target": target_val,
                        "other": other_val
                    }
                else:
                    comparison["differences"][field] = {
                        "target": target_val,
                        "other": other_val
                    }
        
        # Calculate similarity score
        if total_fields > 0:
            comparison["similarity_score"] = (matches / total_fields) * 100
            
            if comparison["similarity_score"] >= 80:
                comparison["match_confidence"] = "High"
            elif comparison["similarity_score"] >= 60:
                comparison["match_confidence"] = "Medium"
            else:
                comparison["match_confidence"] = "Low"
        
        # Compare dimensions
        target_dims = target_data.get("dimensions", {})
        other_dims = other_product_data.get("dimensions", {})
        
        if target_dims and other_dims:
            dim_matches = 0
            dim_total = 0
            
            for dim in ["length", "width", "height", "weight"]:
                if target_dims.get(dim) and other_dims.get(dim):
                    dim_total += 1
                    if abs(float(target_dims[dim]) - float(other_dims[dim])) < 1.0:  # Within 1 unit
                        dim_matches += 1
            
            if dim_total > 0:
                comparison["dimension_similarity"] = (dim_matches / dim_total) * 100
        
        return comparison

# Demo function
def demo_target_parser():
    """Demonstrate Target parser capabilities with the provided HTML file."""
    print("=== Target Product Parser Demo ===\n")
    
    # Read the Target HTML file
    try:
        with open("target_product_details.html", "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print("Error: target_product_details.html not found")
        return
    
    # Initialize parser
    parser = TargetProductParser()
    
    # Parse the HTML
    print("Parsing Target product page...")
    result = parser.parse_html(html_content)
    
    if "error" in result:
        print(f"❌ Parsing failed: {result['error']}")
        return
    
    print("✅ Successfully parsed Target product!\n")
    
    # Display key information
    basic_info = result.get("basic_info", {})
    pricing = result.get("pricing", {})
    physical = result.get("physical_attributes", {})
    reviews = result.get("reviews", {})
    
    print(f"📦 Product: {basic_info.get('name', 'N/A')}")
    print(f"🏷️  Brand: {basic_info.get('brand', 'N/A')}")
    print(f"🆔 TCIN: {basic_info.get('tcin', 'N/A')}")
    print(f"🔢 UPC: {basic_info.get('upc', 'N/A')}")
    print(f"💰 Price: {pricing.get('formatted_current_price', 'N/A')} (reg: {pricing.get('formatted_regular_price', 'N/A')})")
    print(f"📏 Dimensions: {physical.get('dimensions_combined', 'N/A')}")
    print(f"⚖️  Weight: {physical.get('weight', 'N/A')} {physical.get('weight_unit', '')}")
    print(f"⭐ Rating: {reviews.get('average_rating', 'N/A')} ({reviews.get('total_reviews', 0)} reviews)")
    print(f"📊 Total Specifications: {basic_info.get('total_specifications', 0)}")
    
    # Show specifications breakdown
    tech_specs = result.get("technical_specs", {}).get("specifications", {})
    if tech_specs:
        print(f"\n🔧 Key Specifications:")
        for key, value in list(tech_specs.items())[:5]:  # Show first 5
            print(f"   • {key}: {value}")
        if len(tech_specs) > 5:
            print(f"   ... and {len(tech_specs) - 5} more specifications")
    
    # Show features
    features = result.get("product_details", {}).get("features", [])
    highlights = result.get("product_details", {}).get("highlights", [])
    all_features = features + highlights
    
    if all_features:
        print(f"\n✨ Product Features:")
        for feature in all_features[:3]:  # Show first 3
            print(f"   • {feature[:100]}{'...' if len(feature) > 100 else ''}")
        if len(all_features) > 3:
            print(f"   ... and {len(all_features) - 3} more features")
    
    # Show variations
    variations = result.get("variations", {}).get("color_variations", [])
    if variations:
        print(f"\n🎨 Available Colors:")
        for var in variations:
            print(f"   • {var.get('color', 'N/A')} (TCIN: {var.get('tcin', 'N/A')})")
    
    print(f"\n📄 Comparison Data Available: ✅")
    comparison_data = parser.get_comparison_data()
    print(f"   Platform: {comparison_data.get('platform')}")
    print(f"   Specifications Count: {comparison_data.get('total_specs')}")
    print(f"   Ready for Cross-Platform Matching: ✅")
    
    return result

if __name__ == "__main__":
    demo_target_parser()
