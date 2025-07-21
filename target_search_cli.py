#!/usr/bin/env python3
"""
Simple Target.com Search CLI
Quick and easy product search with any keyword
"""

import sys
import json
import argparse
from dynamic_target_scraper import TargetScraper, logger

def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            "proxy": {"enabled": False, "url": ""},
            "location": {
                "zip": "20109", "state": "VA", 
                "latitude": "38.800", "longitude": "-77.550", 
                "store_id": "2323"
            },
            "scraping": {"min_delay": 1, "max_delay": 3}
        }

def search_target(search_term, max_products=25, use_proxy=True, proxy_url=None):
    """Search Target.com for products"""
    
    # Initialize scraper
    scraper = TargetScraper(proxy=proxy_url, use_proxy=use_proxy)
    
    print(f"🔍 Searching Target.com for: '{search_term}'")
    print(f"📦 Max products: {max_products}")
    print(f"🌐 Using proxy: {use_proxy}")
    print("-" * 50)
    
    # Search and extract
    products = scraper.search_and_extract(search_term, max_products)
    
    if not products:
        print("❌ No products found!")
        return
    
    print(f"✅ Found {len(products)} products!\n")
    
    # Display results
    for i, product in enumerate(products, 1):
        print(f"{i:2d}. {product.title[:80]}...")
        if product.price:
            price_info = product.price
            if product.original_price and product.original_price != product.price:
                price_info += f" (was {product.original_price})"
            print(f"    💰 {price_info}")
        
        if product.brand:
            print(f"    🏷️  {product.brand}")
        
        if product.rating:
            stars = "⭐" * int(product.rating)
            print(f"    {stars} {product.rating:.1f}")
            if product.review_count:
                print(f"    📝 {product.review_count} reviews")
        
        print(f"    📍 {product.availability}")
        
        if product.product_url:
            print(f"    🔗 {product.product_url}")
        
        print()
    
    print(f"💾 Results saved to file!")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Search Target.com for products")
    parser.add_argument("search_term", help="Product search term/keyword")
    parser.add_argument("-n", "--max", type=int, default=25, help="Maximum number of products (default: 25)")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy usage")
    parser.add_argument("--config", default="config.json", help="Config file path")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Determine proxy settings
    use_proxy = not args.no_proxy and config.get("proxy", {}).get("enabled", False)
    proxy_url = config.get("proxy", {}).get("url") if use_proxy else None
    
    try:
        search_target(
            search_term=args.search_term,
            max_products=args.max,
            use_proxy=use_proxy,
            proxy_url=proxy_url
        )
    except KeyboardInterrupt:
        print("\n🛑 Search cancelled by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # If no arguments provided, show interactive prompt
    if len(sys.argv) == 1:
        print("🎯 Target.com Product Search")
        print("=" * 30)
        
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("No search term provided!")
            sys.exit(1)
        
        try:
            max_products = int(input("Max products (default 25): ") or "25")
        except ValueError:
            max_products = 25
        
        use_proxy_input = input("Use proxy? (y/n, default y): ").strip().lower()
        use_proxy = use_proxy_input != 'n'
        
        config = load_config()
        proxy_url = config.get("proxy", {}).get("url") if use_proxy else None
        
        try:
            search_target(search_term, max_products, use_proxy, proxy_url)
        except KeyboardInterrupt:
            print("\n🛑 Search cancelled")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        main()
