#!/usr/bin/env python3
"""
Complete demonstration of the enhanced Amazon product parser
Shows all extracted data and matching capabilities
"""
import json
from enhanced_amazon_parser import EnhancedAmazonProductParser, compare_products

def demonstrate_parser():
    """Demonstrate the complete capabilities of the enhanced parser"""
    parser = EnhancedAmazonProductParser()
    
    print("🛍️ Enhanced Amazon Product Parser Demonstration")
    print("=" * 60)
    print("✅ Now capturing ALL product specifications for cross-platform matching!")
    print()
    
    # Parse both products
    products = []
    test_files = ["amazon_response.html", "amazon_response1.html"]
    
    for i, file_name in enumerate(test_files, 1):
        print(f"🔍 Parsing Product {i}: {file_name}")
        print("-" * 40)
        
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            product_data = parser.parse(html_content)
            products.append(product_data)
            
            # Display key information
            print(f"📦 Title: {product_data.get('title', 'N/A')[:60]}...")
            print(f"🏷️  Brand: {product_data.get('brand', 'N/A')}")
            print(f"🔢 ASIN: {product_data.get('asin', 'N/A')}")
            print(f"💰 Price: {product_data.get('pricing', {}).get('current_price', 'N/A')}")
            
            # Show specification count
            specs = product_data.get('specifications', {})
            print(f"📋 Specifications: {len(specs)} detailed fields extracted")
            
            # Show some key specs for matching
            key_specs = ['UPC', 'Brand', 'Color', 'Product Dimensions', 'Item Weight', 'Global Trade Identification Number']
            print(f"🔍 Key Matching Fields:")
            for spec in key_specs:
                if spec in specs:
                    value = specs[spec]
                    if len(str(value)) > 30:
                        value = str(value)[:30] + "..."
                    print(f"   • {spec}: {value}")
            
            # Show physical attributes
            physical = product_data.get('physical_attributes', {})
            if physical:
                print(f"📏 Physical Attributes: {len(physical)} extracted")
                if 'dimensions' in physical:
                    dims = physical['dimensions']
                    print(f"   • Dimensions: {dims.get('depth', 'N/A')}\" x {dims.get('width', 'N/A')}\" x {dims.get('height', 'N/A')}\"")
                if 'weight' in physical:
                    weight = physical['weight']
                    print(f"   • Weight: {weight.get('value', 'N/A')} {weight.get('unit', '')}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing {file_name}: {str(e)}")
            print()
    
    # Demonstrate product comparison if we have two products
    if len(products) == 2:
        print("🔄 Product Comparison Analysis")
        print("-" * 40)
        comparison = compare_products(products[0], products[1])
        
        print(f"🎯 Similarity Score: {comparison.get('similarity_score', 0):.2%}")
        print(f"📊 Matching Fields: {len(comparison.get('matching_fields', []))}")
        print(f"⚠️  Differing Fields: {len(comparison.get('differing_fields', []))}")
        
        # Show some matching fields
        matching_fields = comparison.get('matching_fields', [])
        if matching_fields:
            print("\n✅ Matching Specifications:")
            for field in matching_fields[:5]:  # Show first 5
                print(f"   • {field}")
            if len(matching_fields) > 5:
                print(f"   ... and {len(matching_fields) - 5} more")
        
        # Show differing fields
        differing_fields = comparison.get('differing_fields', [])
        if differing_fields:
            print("\n❌ Different Specifications:")
            for field in differing_fields[:5]:  # Show first 5
                print(f"   • {field}")
            if len(differing_fields) > 5:
                print(f"   ... and {len(differing_fields) - 5} more")
    
    print("\n" + "=" * 60)
    print("🎉 Demonstration completed!")
    print("💪 The parser now extracts comprehensive product data for accurate cross-platform matching!")
    print("\n📝 Key Features:")
    print("   ✅ Complete product specification tables")
    print("   ✅ Physical attributes with parsed dimensions")
    print("   ✅ Product identifiers (UPC, GTIN, ASIN)")
    print("   ✅ Pricing and availability information")
    print("   ✅ Cross-platform matching capabilities")
    print("   ✅ Handles missing/varying fields gracefully")

if __name__ == "__main__":
    demonstrate_parser()
