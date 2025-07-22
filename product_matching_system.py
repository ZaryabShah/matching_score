#!/usr/bin/env python3
"""
Comprehensive Product Matching System

This system performs the following workflow:
1. Search Amazon for products with keywords/UPC/model numbers
2. Select a product and fetch detailed information using Amazon fetcher parser
3. Extract keywords from Amazon product to search Target
4. Fetch detailed Target product information using Target fetcher parser
5. Compare products using sophisticated scoring system
6. Generate matching reports

Usage: python product_matching_system.py "search_term" [--max-results 10]
"""

import os
import sys
import json
import time
import argparse
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Check for curl_cffi availability (used by scrapers)
try:
    import curl_cffi.requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    print("⚠️  curl_cffi not available. Some scraping features may be limited.")

# Import existing modules
from amazon_complete_fetcher_parser import AmazonProductExtractor
from target_complete_fetcher_parser import TargetProductExtractor

# Try to import Amazon search capabilities
try:
    from unneeded.realtime_amazon_extractor import RealTimeAmazonExtractor
    AMAZON_SEARCH_AVAILABLE = True
except ImportError:
    AMAZON_SEARCH_AVAILABLE = False
    print("⚠️  Amazon search module not available. Will work with ASIN only.")

# Try to import Target search capabilities
try:
    from unneeded.dynamic_target_scraper import TargetScraper
    TARGET_SEARCH_AVAILABLE = True
except ImportError:
    TARGET_SEARCH_AVAILABLE = False
    print("⚠️  Target search module not available. Will work with URLs only.")


@dataclass
class MatchingResult:
    """Data class for product matching results"""
    amazon_product: Dict[str, Any]
    target_product: Dict[str, Any]
    match_score: float
    score_breakdown: Dict[str, Any]
    confidence: str
    timestamp: datetime


class ProxyConfig:
    """Centralized proxy configuration"""
    DEFAULT_PROXY = "http://250621Ev04e-resi_region-US_California:5PjDM1IoS0JSr2c@ca.proxy-jet.io:1010"
    
    @staticmethod
    def get_proxy_config() -> Dict[str, str]:
        """Get proxy configuration for requests"""
        return {
            "http": ProxyConfig.DEFAULT_PROXY,
            "https": ProxyConfig.DEFAULT_PROXY
        }


class ProductMatchingScorer:
    """
    Sophisticated product matching scorer with weighted attributes.
    
    Scoring System:
    - UPC/GTIN/EAN Match: 100 points (Perfect identifier match)
    - Model Number Match: 80 points (High confidence)
    - Brand Match: 40 points (Essential for product identification)
    - Title Similarity (>90%): 70 points
    - Title Similarity (>70%): 50 points  
    - Title Similarity (>50%): 30 points
    - Dimensions Match (exact): 60 points
    - Dimensions Match (±5%): 40 points
    - Weight Match (exact): 50 points
    - Weight Match (±10%): 30 points
    - Price Match (±20%): 25 points
    - Category Match: 20 points
    - Color Match: 15 points
    - Material Match: 15 points
    - Feature Keywords Match: 1-10 points per keyword
    """
    
    def __init__(self):
        self.scoring_weights = {
            'upc_match': 100,
            'model_match': 80,
            'brand_match': 40,
            'title_similarity_high': 70,  # >90%
            'title_similarity_medium': 50,  # >70%
            'title_similarity_low': 30,  # >50%
            'dimensions_exact': 60,
            'dimensions_close': 40,  # ±5%
            'weight_exact': 50,
            'weight_close': 30,  # ±10%
            'price_match': 25,  # ±20%
            'category_match': 20,
            'color_match': 15,
            'material_match': 15,
            'feature_keyword': 5  # per matching keyword
        }
    
    def calculate_match_score(self, amazon_product: Dict, target_product: Dict) -> Tuple[float, Dict]:
        """
        Calculate comprehensive matching score between Amazon and Target products.
        
        Returns:
            Tuple of (total_score, score_breakdown)
        """
        score_breakdown = {}
        total_score = 0.0
        
        # 1. UPC/GTIN/EAN Match (Highest Priority)
        upc_score = self._check_upc_match(amazon_product, target_product)
        if upc_score > 0:
            total_score += upc_score
            score_breakdown['upc_match'] = upc_score
        
        # 2. Model Number Match
        model_score = self._check_model_match(amazon_product, target_product)
        if model_score > 0:
            total_score += model_score
            score_breakdown['model_match'] = model_score
        
        # 3. Brand Match
        brand_score = self._check_brand_match(amazon_product, target_product)
        if brand_score > 0:
            total_score += brand_score
            score_breakdown['brand_match'] = brand_score
        
        # 4. Title Similarity
        title_score = self._check_title_similarity(amazon_product, target_product)
        if title_score > 0:
            total_score += title_score
            score_breakdown['title_similarity'] = title_score
        
        # 5. Physical Dimensions
        dimension_score = self._check_dimensions_match(amazon_product, target_product)
        if dimension_score > 0:
            total_score += dimension_score
            score_breakdown['dimensions_match'] = dimension_score
        
        # 6. Weight Match
        weight_score = self._check_weight_match(amazon_product, target_product)
        if weight_score > 0:
            total_score += weight_score
            score_breakdown['weight_match'] = weight_score
        
        # 7. Price Comparison
        price_score = self._check_price_match(amazon_product, target_product)
        if price_score > 0:
            total_score += price_score
            score_breakdown['price_match'] = price_score
        
        # 8. Category Match
        category_score = self._check_category_match(amazon_product, target_product)
        if category_score > 0:
            total_score += category_score
            score_breakdown['category_match'] = category_score
        
        # 9. Color Match
        color_score = self._check_color_match(amazon_product, target_product)
        if color_score > 0:
            total_score += color_score
            score_breakdown['color_match'] = color_score
        
        # 10. Material Match
        material_score = self._check_material_match(amazon_product, target_product)
        if material_score > 0:
            total_score += material_score
            score_breakdown['material_match'] = material_score
        
        # 11. Feature Keywords Match
        feature_score = self._check_feature_keywords(amazon_product, target_product)
        if feature_score > 0:
            total_score += feature_score
            score_breakdown['feature_keywords'] = feature_score
        
        return total_score, score_breakdown
    
    def _extract_text_safely(self, product: Dict, keys: List[str]) -> str:
        """Safely extract text from nested product data"""
        text = ""
        for key_path in keys:
            try:
                keys_list = key_path.split('.')
                value = product
                for k in keys_list:
                    if isinstance(value, dict):
                        value = value.get(k, "")
                    else:
                        value = ""
                        break
                if value and isinstance(value, str):
                    text += f" {value}"
            except:
                continue
        return text.strip().lower()
    
    def _check_upc_match(self, amazon: Dict, target: Dict) -> float:
        """Check UPC/GTIN/EAN match"""
        amazon_upc = self._extract_text_safely(amazon, [
            'specifications.upc', 'specifications.gtin', 'specifications.ean',
            'identifiers.upc', 'identifiers.gtin', 'identifiers.ean',
            'basic_info.upc', 'basic_info.gtin'
        ])
        
        target_upc = self._extract_text_safely(target, [
            'basic_info.upc', 'basic_info.gtin', 
            'technical_specs.specifications.upc',
            'product_details.upc'
        ])
        
        if amazon_upc and target_upc and len(amazon_upc) > 8:
            if amazon_upc == target_upc:
                return self.scoring_weights['upc_match']
        
        return 0
    
    def _check_model_match(self, amazon: Dict, target: Dict) -> float:
        """Check model number match"""
        amazon_model = self._extract_text_safely(amazon, [
            'specifications.model_number', 'specifications.model', 
            'identifiers.model_number', 'basic_info.model_number'
        ])
        
        target_model = self._extract_text_safely(target, [
            'basic_info.model_number', 'technical_specs.specifications.model_number',
            'product_details.model'
        ])
        
        if amazon_model and target_model and len(amazon_model) > 3:
            # Exact match
            if amazon_model == target_model:
                return self.scoring_weights['model_match']
            # Partial match (model contained in each other)
            elif amazon_model in target_model or target_model in amazon_model:
                return self.scoring_weights['model_match'] * 0.7
        
        return 0
    
    def _check_brand_match(self, amazon: Dict, target: Dict) -> float:
        """Check brand match"""
        amazon_brand = self._extract_text_safely(amazon, ['brand', 'basic_info.brand'])
        target_brand = self._extract_text_safely(target, ['basic_info.brand', 'brand'])
        
        if amazon_brand and target_brand:
            if amazon_brand == target_brand:
                return self.scoring_weights['brand_match']
            # Similar brands (common abbreviations/variations)
            elif self._brands_similar(amazon_brand, target_brand):
                return self.scoring_weights['brand_match'] * 0.8
        
        return 0
    
    def _brands_similar(self, brand1: str, brand2: str) -> bool:
        """Check if brands are similar variations"""
        brand_mappings = {
            'amazon basics': ['amazonbasics', 'amazon', 'basics'],
            'best office': ['bestoffice'],
            'sony': ['sony corporation'],
            # Add more brand variations as needed
        }
        
        b1, b2 = brand1.lower().strip(), brand2.lower().strip()
        
        for canonical, variations in brand_mappings.items():
            if (b1 == canonical or b1 in variations) and (b2 == canonical or b2 in variations):
                return True
        
        return False
    
    def _check_title_similarity(self, amazon: Dict, target: Dict) -> float:
        """Check title similarity using advanced text comparison"""
        amazon_title = self._extract_text_safely(amazon, ['title', 'basic_info.name'])
        target_title = self._extract_text_safely(target, ['basic_info.name', 'title'])
        
        if not amazon_title or not target_title:
            return 0
        
        # Clean and normalize titles
        amazon_clean = self._normalize_title(amazon_title)
        target_clean = self._normalize_title(target_title)
        
        # Calculate similarity using multiple methods
        similarity = self._calculate_text_similarity(amazon_clean, target_clean)
        
        if similarity >= 0.9:
            return self.scoring_weights['title_similarity_high']
        elif similarity >= 0.7:
            return self.scoring_weights['title_similarity_medium']  
        elif similarity >= 0.5:
            return self.scoring_weights['title_similarity_low']
        
        return 0
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        # Remove common noise words and normalize
        noise_words = ['for', 'with', 'and', 'the', 'a', 'an', 'in', 'on', 'at', 'by', 'of']
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', ' ', title.lower())
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        # Remove noise words
        words = [w for w in normalized.split() if w not in noise_words and len(w) > 2]
        
        return ' '.join(words)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using token-based approach"""
        if not text1 or not text2:
            return 0.0
        
        # Tokenize
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())
        
        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _check_dimensions_match(self, amazon: Dict, target: Dict) -> float:
        """Check physical dimensions match"""
        amazon_dims = self._extract_dimensions(amazon)
        target_dims = self._extract_dimensions(target)
        
        if not amazon_dims or not target_dims:
            return 0
        
        # Compare dimensions with tolerance
        if self._dimensions_match(amazon_dims, target_dims, tolerance=0.0):
            return self.scoring_weights['dimensions_exact']
        elif self._dimensions_match(amazon_dims, target_dims, tolerance=0.05):
            return self.scoring_weights['dimensions_close']
        
        return 0
    
    def _extract_dimensions(self, product: Dict) -> Optional[Dict[str, float]]:
        """Extract dimensions from product data"""
        try:
            # Try multiple paths for dimensions
            dim_paths = [
                'physical_attributes',
                'specifications.dimensions',
                'technical_specs.specifications'
            ]
            
            for path in dim_paths:
                dims_data = self._get_nested_value(product, path)
                if dims_data:
                    extracted = {}
                    # Look for length, width, height
                    for key in ['length', 'width', 'height']:
                        if key in dims_data:
                            try:
                                extracted[key] = float(dims_data[key])
                            except:
                                continue
                    
                    if len(extracted) >= 2:  # At least 2 dimensions
                        return extracted
            
            return None
        except:
            return None
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                value = value[key]
            return value
        except:
            return None
    
    def _dimensions_match(self, dims1: Dict, dims2: Dict, tolerance: float = 0.05) -> bool:
        """Check if dimensions match within tolerance"""
        common_keys = set(dims1.keys()).intersection(set(dims2.keys()))
        if len(common_keys) < 2:
            return False
        
        for key in common_keys:
            val1, val2 = dims1[key], dims2[key]
            if val1 == 0 or val2 == 0:
                continue
                
            diff = abs(val1 - val2) / max(val1, val2)
            if diff > tolerance:
                return False
        
        return True
    
    def _check_weight_match(self, amazon: Dict, target: Dict) -> float:
        """Check weight match"""
        amazon_weight = self._extract_weight(amazon)
        target_weight = self._extract_weight(target)
        
        if not amazon_weight or not target_weight:
            return 0
        
        diff = abs(amazon_weight - target_weight) / max(amazon_weight, target_weight)
        
        if diff == 0:
            return self.scoring_weights['weight_exact']
        elif diff <= 0.1:  # ±10%
            return self.scoring_weights['weight_close']
        
        return 0
    
    def _extract_weight(self, product: Dict) -> Optional[float]:
        """Extract weight from product data"""
        try:
            weight_paths = [
                'physical_attributes.weight',
                'specifications.weight',
                'technical_specs.specifications.weight'
            ]
            
            for path in weight_paths:
                weight_data = self._get_nested_value(product, path)
                if weight_data:
                    try:
                        return float(weight_data)
                    except:
                        continue
            
            return None
        except:
            return None
    
    def _check_price_match(self, amazon: Dict, target: Dict) -> float:
        """Check price match within tolerance"""
        amazon_price = self._extract_price(amazon)
        target_price = self._extract_price(target)
        
        if not amazon_price or not target_price:
            return 0
        
        diff = abs(amazon_price - target_price) / max(amazon_price, target_price)
        
        if diff <= 0.2:  # ±20%
            return self.scoring_weights['price_match']
        
        return 0
    
    def _extract_price(self, product: Dict) -> Optional[float]:
        """Extract price from product data"""
        try:
            price_paths = [
                'pricing.current_price',
                'pricing.formatted_current_price',
                'pricing.price'
            ]
            
            for path in price_paths:
                price_data = self._get_nested_value(product, path)
                if price_data:
                    # Extract numeric value from price string
                    price_str = str(price_data)
                    price_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
                    if price_match:
                        return float(price_match.group())
            
            return None
        except:
            return None
    
    def _check_category_match(self, amazon: Dict, target: Dict) -> float:
        """Check category match"""
        amazon_cats = self._extract_categories(amazon)
        target_cats = self._extract_categories(target)
        
        if not amazon_cats or not target_cats:
            return 0
        
        # Check for overlap in categories
        common_categories = amazon_cats.intersection(target_cats)
        if common_categories:
            return self.scoring_weights['category_match']
        
        return 0
    
    def _extract_categories(self, product: Dict) -> set:
        """Extract categories from product data"""
        try:
            category_paths = [
                'categories',
                'category_info.category_name',
                'breadcrumbs'
            ]
            
            categories = set()
            for path in category_paths:
                cat_data = self._get_nested_value(product, path)
                if cat_data:
                    if isinstance(cat_data, list):
                        categories.update([str(c).lower() for c in cat_data])
                    else:
                        categories.add(str(cat_data).lower())
            
            return categories
        except:
            return set()
    
    def _check_color_match(self, amazon: Dict, target: Dict) -> float:
        """Check color match"""
        amazon_color = self._extract_color(amazon)
        target_color = self._extract_color(target)
        
        if amazon_color and target_color and amazon_color == target_color:
            return self.scoring_weights['color_match']
        
        return 0
    
    def _extract_color(self, product: Dict) -> Optional[str]:
        """Extract color from product data"""
        try:
            color_paths = [
                'variations.color',
                'specifications.color',
                'product_details.color'
            ]
            
            for path in color_paths:
                color_data = self._get_nested_value(product, path)
                if color_data:
                    return str(color_data).lower()
            
            return None
        except:
            return None
    
    def _check_material_match(self, amazon: Dict, target: Dict) -> float:
        """Check material match"""
        amazon_materials = self._extract_materials(amazon)
        target_materials = self._extract_materials(target)
        
        if amazon_materials and target_materials:
            common_materials = amazon_materials.intersection(target_materials)
            if common_materials:
                return self.scoring_weights['material_match']
        
        return 0
    
    def _extract_materials(self, product: Dict) -> set:
        """Extract materials from product data"""
        try:
            material_paths = [
                'specifications.material',
                'product_details.materials',
                'technical_specs.specifications.material'
            ]
            
            materials = set()
            for path in material_paths:
                mat_data = self._get_nested_value(product, path)
                if mat_data:
                    if isinstance(mat_data, list):
                        materials.update([str(m).lower() for m in mat_data])
                    else:
                        materials.add(str(mat_data).lower())
            
            return materials
        except:
            return set()
    
    def _check_feature_keywords(self, amazon: Dict, target: Dict) -> float:
        """Check feature keywords match"""
        amazon_features = self._extract_features(amazon)
        target_features = self._extract_features(target)
        
        if not amazon_features or not target_features:
            return 0
        
        common_features = amazon_features.intersection(target_features)
        return len(common_features) * self.scoring_weights['feature_keyword']
    
    def _extract_features(self, product: Dict) -> set:
        """Extract feature keywords from product data"""
        try:
            feature_paths = [
                'specifications',
                'product_details.highlights',
                'technical_specs.specifications'
            ]
            
            features = set()
            for path in feature_paths:
                feat_data = self._get_nested_value(product, path)
                if feat_data:
                    if isinstance(feat_data, dict):
                        for k, v in feat_data.items():
                            features.add(str(k).lower())
                            features.add(str(v).lower())
                    elif isinstance(feat_data, list):
                        for item in feat_data:
                            features.add(str(item).lower())
            
            # Clean and filter meaningful features
            cleaned_features = set()
            for feature in features:
                if len(feature) > 3 and not feature.isdigit():
                    cleaned_features.add(feature)
            
            return cleaned_features
        except:
            return set()
    
    def get_confidence_level(self, score: float) -> str:
        """Get confidence level based on score"""
        if score >= 150:
            return "Very High"
        elif score >= 100:
            return "High" 
        elif score >= 70:
            return "Medium"
        elif score >= 40:
            return "Low"
        else:
            return "Very Low"


class ProductMatchingSystem:
    """Main system orchestrating the entire product matching workflow"""
    
    def __init__(self, proxy_config: Optional[Dict] = None):
        """Initialize the product matching system"""
        self.proxy_config = proxy_config or {"url": ProxyConfig.DEFAULT_PROXY}
        
        # Initialize components
        self.amazon_extractor = AmazonProductExtractor()
        self.target_extractor = TargetProductExtractor()
        self.scorer = ProductMatchingScorer()
        
        # Initialize search modules if available
        if AMAZON_SEARCH_AVAILABLE:
            self.amazon_searcher = RealTimeAmazonExtractor(self.proxy_config)
        
        if TARGET_SEARCH_AVAILABLE:
            self.target_searcher = TargetScraper(
                proxy=self.proxy_config.get('url'),
                use_proxy=True
            )
        
        # Results storage
        self.results_dir = Path("matching_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def run_complete_matching_workflow(self, search_term: str, max_results: int = 5) -> List[MatchingResult]:
        """
        Run the complete product matching workflow.
        
        Args:
            search_term: Search term for products
            max_results: Maximum number of Target products to compare
            
        Returns:
            List of MatchingResult objects
        """
        print(f"🚀 Starting product matching workflow for: '{search_term}'")
        print("=" * 60)
        
        # Step 1: Search Amazon and select first product
        print("📦 Step 1: Searching Amazon...")
        amazon_product = self._search_and_get_amazon_product(search_term)
        
        if not amazon_product:
            print("❌ No Amazon product found or fetched.")
            return []
        
        print(f"✅ Found Amazon product: {amazon_product.get('title', 'Unknown')[:100]}...")
        
        # Step 2: Extract keywords and search Target
        print("\n🎯 Step 2: Searching Target with extracted keywords...")
        target_search_terms = self._extract_target_search_keywords(amazon_product)
        target_products = []
        
        for search_term in target_search_terms[:3]:  # Try top 3 search terms
            print(f"   🔍 Searching Target for: '{search_term}'")
            products = self._search_target_products(search_term, max_results)
            target_products.extend(products)
            if len(target_products) >= max_results:
                break
        
        # Remove duplicates
        seen_urls = set()
        unique_target_products = []
        for product in target_products:
            url = product.get('product_url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_target_products.append(product)
        
        target_products = unique_target_products[:max_results]
        
        if not target_products:
            print("❌ No Target products found.")
            return []
        
        print(f"✅ Found {len(target_products)} Target product(s) to compare")
        
        # Step 3: Fetch detailed Target product information
        print("\n📊 Step 3: Fetching detailed Target product information...")
        detailed_target_products = []
        
        for i, product in enumerate(target_products, 1):
            product_url = product.get('product_url')
            if not product_url:
                continue
                
            print(f"   📋 Fetching details for Target product {i}/{len(target_products)}...")
            detailed_product = self._fetch_target_product_details(product_url)
            
            if detailed_product and 'error' not in detailed_product:
                detailed_target_products.append(detailed_product)
            
            # Rate limiting
            time.sleep(2)
        
        print(f"✅ Successfully fetched details for {len(detailed_target_products)} Target product(s)")
        
        # Step 4: Compare and score products
        print("\n🔬 Step 4: Comparing and scoring products...")
        matching_results = []
        
        for i, target_product in enumerate(detailed_target_products, 1):
            print(f"   ⚖️  Comparing with Target product {i}/{len(detailed_target_products)}...")
            
            score, score_breakdown = self.scorer.calculate_match_score(
                amazon_product, target_product
            )
            
            confidence = self.scorer.get_confidence_level(score)
            
            matching_result = MatchingResult(
                amazon_product=amazon_product,
                target_product=target_product,
                match_score=score,
                score_breakdown=score_breakdown,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
            matching_results.append(matching_result)
            
            print(f"   📊 Match Score: {score:.1f} ({confidence} confidence)")
        
        # Step 5: Sort by score and generate report
        matching_results.sort(key=lambda x: x.match_score, reverse=True)
        
        print("\n📈 Step 5: Generating matching report...")
        self._generate_matching_report(search_term, matching_results)
        
        print(f"\n🎉 Workflow completed! Found {len(matching_results)} product comparisons.")
        
        return matching_results
    
    def _search_and_get_amazon_product(self, search_term: str) -> Optional[Dict]:
        """Search Amazon and get detailed product information for the first result"""
        try:
            if not AMAZON_SEARCH_AVAILABLE:
                print("⚠️  Amazon search not available. Please provide ASIN directly.")
                return None
            
            # Search Amazon
            search_results = self.amazon_searcher.search_and_extract(search_term, max_pages=1)
            products = search_results.get('products', [])
            
            if not products:
                print("❌ No products found in Amazon search.")
                return None
            
            # Get first product's ASIN
            first_product = products[0]
            asin = first_product.get('asin')
            
            if not asin:
                print("❌ No ASIN found for first product.")
                return None
            
            print(f"   📦 Selected product ASIN: {asin}")
            
            # Fetch detailed information
            detailed_product = self.amazon_extractor.extract_product(asin)
            
            if 'error' in detailed_product:
                print(f"❌ Error fetching Amazon product details: {detailed_product['error']}")
                return None
            
            return detailed_product
            
        except Exception as e:
            print(f"❌ Error in Amazon search/fetch: {str(e)}")
            return None
    
    def _extract_target_search_keywords(self, amazon_product: Dict) -> List[str]:
        """Extract relevant keywords from Amazon product for Target search"""
        keywords = []
        
        # Primary keywords from title
        title = amazon_product.get('title', '')
        if title:
            # Extract important words from title (skip common words)
            title_words = self._extract_meaningful_words(title)
            
            # Create combinations of 2-4 words
            for length in [4, 3, 2]:
                for i in range(len(title_words) - length + 1):
                    phrase = ' '.join(title_words[i:i+length])
                    if len(phrase) > 10:  # Minimum length
                        keywords.append(phrase)
        
        # Brand + product type
        brand = amazon_product.get('brand', '')
        if brand:
            categories = amazon_product.get('categories', [])
            if categories:
                main_category = categories[0] if categories else ''
                if main_category:
                    keywords.append(f"{brand} {main_category}")
            
            # Brand + key title words
            if title:
                key_words = title_words[:3]  # First 3 meaningful words
                keywords.append(f"{brand} {' '.join(key_words)}")
        
        # Model number search
        model_number = amazon_product.get('specifications', {}).get('model_number', '')
        if not model_number:
            model_number = amazon_product.get('identifiers', {}).get('model_number', '')
        
        if model_number and len(model_number) > 3:
            keywords.append(model_number)
            if brand:
                keywords.append(f"{brand} {model_number}")
        
        # UPC search if available
        upc = amazon_product.get('specifications', {}).get('upc', '')
        if not upc:
            upc = amazon_product.get('identifiers', {}).get('upc', '')
        
        if upc and len(upc) > 8:
            keywords.append(upc)
        
        # Remove duplicates and sort by length (longer first)
        unique_keywords = list(set(keywords))
        unique_keywords.sort(key=len, reverse=True)
        
        return unique_keywords[:10]  # Top 10 keywords
    
    def _extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful words from text, filtering out noise"""
        import string
        
        # Common stop words to remove
        stop_words = {
            'for', 'with', 'and', 'the', 'a', 'an', 'in', 'on', 'at', 'by', 'of',
            'to', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those'
        }
        
        # Clean and normalize
        text = text.lower()
        text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
        words = text.split()
        
        # Filter meaningful words
        meaningful_words = []
        for word in words:
            if (len(word) > 2 and 
                word not in stop_words and 
                not word.isdigit() and
                word.isalpha()):
                meaningful_words.append(word)
        
        return meaningful_words
    
    def _search_target_products(self, search_term: str, max_results: int = 5) -> List[Dict]:
        """Search Target for products"""
        try:
            if not TARGET_SEARCH_AVAILABLE:
                print("⚠️  Target search not available.")
                return []
            
            # Search Target
            products = self.target_searcher.search_and_extract(search_term, max_results)
            
            if not products:
                return []
            
            # Convert to dict format
            product_dicts = []
            for product in products:
                product_dict = {
                    'tcin': product.tcin,
                    'title': product.title,
                    'price': product.price,
                    'original_price': product.original_price,
                    'brand': product.brand,
                    'product_url': product.product_url,
                    'availability': product.availability
                }
                product_dicts.append(product_dict)
            
            return product_dicts
            
        except Exception as e:
            print(f"❌ Error searching Target: {str(e)}")
            return []
    
    def _fetch_target_product_details(self, product_url: str) -> Optional[Dict]:
        """Fetch detailed Target product information"""
        try:
            detailed_product = self.target_extractor.extract_product(product_url)
            return detailed_product
        except Exception as e:
            print(f"❌ Error fetching Target product details: {str(e)}")
            return None
    
    def _generate_matching_report(self, search_term: str, results: List[MatchingResult]) -> None:
        """Generate comprehensive matching report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"matching_report_{search_term.replace(' ', '_')}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        # Prepare report data
        report_data = {
            'search_term': search_term,
            'timestamp': timestamp,
            'total_comparisons': len(results),
            'amazon_product': {
                'title': results[0].amazon_product.get('title', '') if results else '',
                'asin': results[0].amazon_product.get('asin', '') if results else '',
                'brand': results[0].amazon_product.get('brand', '') if results else ''
            },
            'comparisons': []
        }
        
        for i, result in enumerate(results):
            comparison = {
                'rank': i + 1,
                'target_product': {
                    'title': result.target_product.get('basic_info', {}).get('name', ''),
                    'tcin': result.target_product.get('basic_info', {}).get('tcin', ''),
                    'brand': result.target_product.get('basic_info', {}).get('brand', ''),
                    'price': result.target_product.get('pricing', {}).get('formatted_current_price', '')
                },
                'match_score': result.match_score,
                'confidence': result.confidence,
                'score_breakdown': result.score_breakdown
            }
            report_data['comparisons'].append(comparison)
        
        # Save report
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Report saved: {filepath}")
        
        # Print summary
        print("\n📋 MATCHING SUMMARY:")
        print(f"   Search term: {search_term}")
        print(f"   Total comparisons: {len(results)}")
        
        if results:
            best_match = results[0]
            print(f"   Best match: {best_match.target_product.get('basic_info', {}).get('name', '')[:60]}...")
            print(f"   Best score: {best_match.match_score:.1f} ({best_match.confidence})")
            
            print("\n   Score breakdown:")
            for category, score in best_match.score_breakdown.items():
                print(f"     {category}: {score:.1f}")


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Comprehensive Product Matching System")
    parser.add_argument("search_term", help="Search term for products")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of Target products to compare (default: 5)")
    parser.add_argument("--asin", help="Use specific Amazon ASIN instead of searching")
    parser.add_argument("--target-urls", nargs="*", help="Specific Target URLs to compare against")
    
    args = parser.parse_args()
    
    # Initialize system
    system = ProductMatchingSystem()
    
    if args.asin and args.target_urls:
        # Direct comparison mode
        print(f"🎯 Direct comparison mode: ASIN {args.asin} vs {len(args.target_urls)} Target products")
        # Implementation for direct comparison would go here
        print("⚠️  Direct comparison mode not implemented yet. Use search mode.")
    else:
        # Full workflow mode
        results = system.run_complete_matching_workflow(
            args.search_term,
            max_results=args.max_results
        )
        
        if results:
            print(f"\n🏆 Best match found with score: {results[0].match_score:.1f}")
        else:
            print("\n❌ No matches found.")


if __name__ == "__main__":
    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        print("🛒 Product Matching System - Interactive Mode")
        print("=" * 50)
        
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("❌ No search term provided!")
            sys.exit(1)
        
        try:
            max_results = int(input("Max Target products to compare (default 5): ") or "5")
        except ValueError:
            max_results = 5
        
        system = ProductMatchingSystem()
        results = system.run_complete_matching_workflow(search_term, max_results)
        
        if results:
            print(f"\n🎉 Found {len(results)} product comparisons!")
            print(f"🏆 Best match score: {results[0].match_score:.1f}")
        else:
            print("\n😞 No matches found.")
    else:
        main()
