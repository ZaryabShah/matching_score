#!/usr/bin/env python3
"""
Amazon Product Data Analyzer

Quick analysis and filtering utilities for parsed Amazon product data.
"""

import json
import statistics
from collections import Counter
from datetime import datetime


class ProductAnalyzer:
    """Analyze and filter parsed Amazon product data."""
    
    def __init__(self, json_file: str):
        """Load product data from JSON file."""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.products = self.data.get('products', [])
    
    def filter_by_price_range(self, min_price: float = 0, max_price: float = float('inf')):
        """Filter products by price range."""
        filtered = []
        for product in self.products:
            price = product.get('pricing', {}).get('current_price', {}).get('amount', 0)
            if min_price <= price <= max_price:
                filtered.append(product)
        return filtered
    
    def filter_by_rating(self, min_rating: float = 0):
        """Filter products by minimum rating."""
        filtered = []
        for product in self.products:
            rating = product.get('reviews', {}).get('rating', {}).get('value', 0)
            if rating >= min_rating:
                filtered.append(product)
        return filtered
    
    def filter_sponsored(self, sponsored_only: bool = True):
        """Filter sponsored or organic products."""
        filtered = []
        for product in self.products:
            is_sponsored = product.get('advertising', {}).get('is_sponsored', False)
            if sponsored_only == is_sponsored:
                filtered.append(product)
        return filtered
    
    def get_brand_analysis(self):
        """Analyze brand distribution."""
        brands = []
        amazon_brands = 0
        
        for product in self.products:
            brand_info = product.get('brand', {})
            brand_name = brand_info.get('name', 'Unknown')
            brands.append(brand_name)
            
            if brand_info.get('is_amazon_brand', False):
                amazon_brands += 1
        
        brand_counts = Counter(brands)
        
        return {
            'total_brands': len(set(brands)),
            'amazon_brands': amazon_brands,
            'top_brands': brand_counts.most_common(10),
            'brand_distribution': dict(brand_counts)
        }
    
    def get_price_analysis(self):
        """Analyze price distribution."""
        prices = []
        discounted = 0
        
        for product in self.products:
            pricing = product.get('pricing', {})
            current_price = pricing.get('current_price', {}).get('amount')
            original_price = pricing.get('original_price', {}).get('amount')
            
            if current_price:
                prices.append(current_price)
                
            if original_price and current_price and original_price > current_price:
                discounted += 1
        
        if prices:
            return {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': round(statistics.mean(prices), 2),
                'median_price': round(statistics.median(prices), 2),
                'discounted_products': discounted,
                'discount_percentage': round((discounted / len(prices)) * 100, 1)
            }
        return {}
    
    def get_rating_analysis(self):
        """Analyze ratings and reviews."""
        ratings = []
        review_counts = []
        
        for product in self.products:
            reviews = product.get('reviews', {})
            rating = reviews.get('rating', {}).get('value')
            count = reviews.get('count', 0)
            
            if rating:
                ratings.append(rating)
            if count:
                review_counts.append(count)
        
        if ratings:
            rating_distribution = Counter([round(r, 1) for r in ratings])
            
            return {
                'avg_rating': round(statistics.mean(ratings), 2),
                'min_rating': min(ratings),
                'max_rating': max(ratings),
                'rating_distribution': dict(rating_distribution),
                'avg_review_count': round(statistics.mean(review_counts), 0) if review_counts else 0,
                'total_reviews': sum(review_counts)
            }
        return {}
    
    def get_shipping_analysis(self):
        """Analyze shipping options."""
        free_shipping = 0
        prime_eligible = 0
        
        for product in self.products:
            shipping = product.get('shipping', {})
            if shipping.get('free_shipping', False):
                free_shipping += 1
            if shipping.get('prime_eligible', False):
                prime_eligible += 1
        
        return {
            'free_shipping_count': free_shipping,
            'free_shipping_percentage': round((free_shipping / len(self.products)) * 100, 1),
            'prime_eligible_count': prime_eligible,
            'prime_eligible_percentage': round((prime_eligible / len(self.products)) * 100, 1)
        }
    
    def export_filtered_data(self, filtered_products: list, filename: str):
        """Export filtered product data to JSON."""
        export_data = {
            'products': filtered_products,
            'total_products': len(filtered_products),
            'filtered_timestamp': datetime.now().isoformat(),
            'original_total': len(self.products)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(filtered_products)} products to {filename}")
    
    def print_product_summary(self, product: dict, index: int = 0):
        """Print a formatted summary of a single product."""
        print(f"\n--- Product {index + 1} ---")
        print(f"ASIN: {product.get('asin', 'N/A')}")
        print(f"Title: {product.get('title', {}).get('short_title', 'N/A')}")
        
        # Price
        pricing = product.get('pricing', {})
        current_price = pricing.get('current_price', {})
        if current_price.get('amount'):
            print(f"Price: ${current_price.get('amount')} {current_price.get('currency', '')}")
        
        # Rating
        reviews = product.get('reviews', {})
        rating = reviews.get('rating', {})
        if rating.get('value'):
            print(f"Rating: {rating.get('value')}/5 ({reviews.get('count', 0)} reviews)")
        
        # Brand and sponsored
        brand = product.get('brand', {})
        print(f"Brand: {brand.get('name', 'N/A')}")
        if product.get('advertising', {}).get('is_sponsored', False):
            print("📺 Sponsored")
        
        # Shipping
        shipping = product.get('shipping', {})
        if shipping.get('free_shipping', False):
            print("🚚 Free Shipping")


def main():
    """Example analysis of parsed product data."""
    # Load the most recent parsed data file
    import glob
    json_files = glob.glob("amazon_products_parsed_*.json")
    if not json_files:
        print("No parsed product data files found!")
        return
    
    latest_file = max(json_files)
    print(f"Analyzing: {latest_file}\n")
    
    analyzer = ProductAnalyzer(latest_file)
    
    print("=== COMPREHENSIVE PRODUCT ANALYSIS ===\n")
    
    # Brand Analysis
    print("🏷️ BRAND ANALYSIS:")
    brand_analysis = analyzer.get_brand_analysis()
    print(f"  Total unique brands: {brand_analysis['total_brands']}")
    print(f"  Amazon brands: {brand_analysis['amazon_brands']}")
    print("  Top 5 brands:")
    for brand, count in brand_analysis['top_brands'][:5]:
        print(f"    {brand}: {count} products")
    
    # Price Analysis
    print("\n💰 PRICE ANALYSIS:")
    price_analysis = analyzer.get_price_analysis()
    if price_analysis:
        print(f"  Price range: ${price_analysis['min_price']} - ${price_analysis['max_price']}")
        print(f"  Average price: ${price_analysis['avg_price']}")
        print(f"  Median price: ${price_analysis['median_price']}")
        print(f"  Discounted products: {price_analysis['discounted_products']} ({price_analysis['discount_percentage']}%)")
    
    # Rating Analysis
    print("\n⭐ RATING ANALYSIS:")
    rating_analysis = analyzer.get_rating_analysis()
    if rating_analysis:
        print(f"  Average rating: {rating_analysis['avg_rating']}/5")
        print(f"  Rating range: {rating_analysis['min_rating']} - {rating_analysis['max_rating']}")
        print(f"  Average reviews per product: {rating_analysis['avg_review_count']}")
        print(f"  Total reviews: {rating_analysis['total_reviews']}")
    
    # Shipping Analysis
    print("\n🚚 SHIPPING ANALYSIS:")
    shipping_analysis = analyzer.get_shipping_analysis()
    print(f"  Free shipping: {shipping_analysis['free_shipping_count']} products ({shipping_analysis['free_shipping_percentage']}%)")
    print(f"  Prime eligible: {shipping_analysis['prime_eligible_count']} products ({shipping_analysis['prime_eligible_percentage']}%)")
    
    # Filtering Examples
    print("\n🔍 FILTERING EXAMPLES:")
    
    # High-rated products
    high_rated = analyzer.filter_by_rating(4.5)
    print(f"  Products rated 4.5+ stars: {len(high_rated)}")
    
    # Budget products
    budget_products = analyzer.filter_by_price_range(0, 100)
    print(f"  Products under $100: {len(budget_products)}")
    
    # Premium products
    premium_products = analyzer.filter_by_price_range(200, 1000)
    print(f"  Products $200-$1000: {len(premium_products)}")
    
    # Sponsored vs Organic
    sponsored = analyzer.filter_sponsored(True)
    organic = analyzer.filter_sponsored(False)
    print(f"  Sponsored products: {len(sponsored)}")
    print(f"  Organic products: {len(organic)}")
    
    # Show top 3 highest-rated products
    print("\n🏆 TOP 3 HIGHEST-RATED PRODUCTS:")
    high_rated_sorted = sorted(high_rated, key=lambda x: x.get('reviews', {}).get('rating', {}).get('value', 0), reverse=True)
    for i, product in enumerate(high_rated_sorted[:3]):
        analyzer.print_product_summary(product, i)
    
    # Export examples
    print(f"\n💾 EXPORT EXAMPLES:")
    analyzer.export_filtered_data(high_rated, f"high_rated_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    analyzer.export_filtered_data(budget_products, f"budget_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")


if __name__ == "__main__":
    main()
