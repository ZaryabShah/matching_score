#!/usr/bin/env python3
"""
Quick test script for the Target scraper
"""

from dynamic_target_scraper import TargetScraper
import json

def test_scraper():
    """Test the scraper with a simple search"""
    print("🧪 Testing Target.com Scraper")
    print("=" * 40)
    
    # Initialize scraper without proxy for testing
    scraper = TargetScraper(use_proxy=False)
    
    # Test search term
    search_term = "wireless headphones"
    max_products = 5
    
    print(f"🔍 Testing search for: '{search_term}'")
    print(f"📦 Max products: {max_products}")
    print("🌐 Proxy: Disabled (for testing)")
    print("-" * 40)
    
    try:
        # Search for TCINs first
        tcins, metadata = scraper.search_products(search_term, limit=max_products)
        
        print(f"✅ Search successful!")
        print(f"📋 Found {len(tcins)} product IDs")
        
        if tcins:
            print(f"🔢 Sample TCINs: {tcins[:3]}")
            
            # Test getting product details
            print("\n🔍 Testing product detail extraction...")
            products = scraper.get_product_details(tcins[:2])  # Test with just 2 products
            
            if products:
                print(f"✅ Product details extracted successfully!")
                print(f"📦 Got details for {len(products)} products")
                
                # Show first product
                product = products[0]
                print(f"\n📋 Sample Product:")
                print(f"   Title: {product.title[:60]}...")
                print(f"   Price: {product.price or 'N/A'}")
                print(f"   Brand: {product.brand or 'N/A'}")
                print(f"   Rating: {product.rating or 'N/A'}")
                print(f"   TCIN: {product.tcin}")
            else:
                print("⚠️ No product details extracted")
        else:
            print("⚠️ No product IDs found")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper()
