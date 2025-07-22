"""
Amazon Product Parser - Usage Examples and Documentation

This module provides comprehensive parsing capabilities for Amazon product pages,
designed specifically for cross-platform product matching and comparison.

Key Features:
- Extracts 15+ categories of product information
- Generates matching fingerprints for product comparison
- Supports multiple ASINs with flexible specification handling
- Cross-platform matching capabilities
- Comprehensive error handling
"""

from enhanced_amazon_parser import EnhancedAmazonProductParser, parse_amazon_product_enhanced, compare_products
import json
from typing import List, Dict, Any


def demo_basic_parsing():
    """Demonstrate basic product parsing"""
    print("=" * 60)
    print("BASIC PRODUCT PARSING DEMO")
    print("=" * 60)
    
    # Parse single product
    parser = EnhancedAmazonProductParser()
    
    # Example with HTML file
    with open("amazon_response.html", 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    product_data = parser.parse(html_content, "https://www.amazon.com/dp/B00FS3VJAO/")
    
    print(f"📦 Product: {product_data['title'][:50]}...")
    print(f"🏷️ Brand: {product_data['brand']}")
    print(f"🆔 ASIN: {product_data['asin']}")
    print(f"💰 Price: {product_data['pricing'].get('current_price', 'N/A')}")
    print(f"⭐ Rating: {product_data['reviews'].get('average_rating', 'N/A')}")
    print(f"📊 Reviews: {product_data['reviews'].get('total_reviews', 'N/A')}")
    print()


def demo_detailed_extraction():
    """Demonstrate detailed product information extraction"""
    print("=" * 60)
    print("DETAILED EXTRACTION DEMO")
    print("=" * 60)
    
    product_data = parse_amazon_product_enhanced("amazon_response.html")
    
    # Display matching identifiers
    matching_data = product_data.get('matching_data', {})
    print("🔍 MATCHING IDENTIFIERS:")
    print(f"   Model Number: {matching_data.get('model_number', 'N/A')}")
    print(f"   Barcode: {matching_data.get('barcode', 'N/A')}")
    print(f"   Brand (normalized): {matching_data.get('brand_normalized', 'N/A')}")
    print(f"   Title Keywords: {matching_data.get('title_keywords', [])}")
    print()
    
    # Physical attributes
    physical = product_data.get('physical_attributes', {})
    print("📐 PHYSICAL ATTRIBUTES:")
    if 'dimensions' in physical:
        dims = physical['dimensions']
        print(f"   Dimensions: {dims.get('length')}x{dims.get('width')}x{dims.get('height')} {dims.get('unit')}")
    if 'weight' in physical:
        weight = physical['weight']
        print(f"   Weight: {weight.get('value')} {weight.get('unit')}")
    if 'color' in physical:
        print(f"   Color: {physical['color']}")
    print()
    
    # Specifications by category
    specs = product_data.get('specifications', {})
    print("📋 SPECIFICATIONS BY CATEGORY:")
    for category, spec_dict in specs.items():
        if spec_dict:
            print(f"   {category.upper()}:")
            for key, value in spec_dict.items():
                print(f"     • {key}: {value[:50]}...")
    print()


def demo_product_comparison():
    """Demonstrate product comparison capabilities"""
    print("=" * 60)
    print("PRODUCT COMPARISON DEMO")
    print("=" * 60)
    
    # Parse two different products
    product1 = parse_amazon_product_enhanced("amazon_response.html")
    product2 = parse_amazon_product_enhanced("amazon_response1.html")
    
    print(f"🆚 COMPARING PRODUCTS:")
    print(f"Product 1: {product1['title'][:50]}...")
    print(f"Product 2: {product2['title'][:50]}...")
    print()
    
    # Compare products
    comparison = compare_products(product1, product2)
    
    print("📊 COMPARISON RESULTS:")
    print(f"   Brand Match: {'✅' if comparison['brand_match'] else '❌'} {comparison['brand_match']}")
    print(f"   Title Similarity: {'✅' if comparison['title_similarity'] > 0.5 else '❌'} {comparison['title_similarity']:.1%}")
    print(f"   Model Match: {'✅' if comparison['model_match'] else '❌'} {comparison['model_match']}")
    print(f"   Dimension Match: {'✅' if comparison['dimension_match'] else '❌'} {comparison['dimension_match']}")
    print(f"   Fingerprint Match: {'✅' if comparison['fingerprint_match'] else '❌'} {comparison['fingerprint_match']}")
    print()
    
    # Overall similarity score
    similarity_score = (
        (1 if comparison['brand_match'] else 0) * 0.3 +
        comparison['title_similarity'] * 0.4 +
        (1 if comparison['model_match'] else 0) * 0.2 +
        (1 if comparison['dimension_match'] else 0) * 0.1
    )
    
    print(f"🎯 OVERALL SIMILARITY: {similarity_score:.1%}")
    if similarity_score > 0.8:
        print("   Status: LIKELY SAME PRODUCT ✅")
    elif similarity_score > 0.6:
        print("   Status: POSSIBLY RELATED PRODUCTS ⚠️")
    else:
        print("   Status: DIFFERENT PRODUCTS ❌")
    print()


def demo_batch_processing():
    """Demonstrate batch processing of multiple products"""
    print("=" * 60)
    print("BATCH PROCESSING DEMO")
    print("=" * 60)
    
    html_files = ["amazon_response.html", "amazon_response1.html"]
    products = []
    
    for html_file in html_files:
        try:
            product_data = parse_amazon_product_enhanced(html_file)
            products.append(product_data)
            print(f"✅ Processed: {html_file}")
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    print(f"\n📦 Successfully processed {len(products)} products")
    
    # Create product summary
    summary = []
    for product in products:
        summary.append({
            'asin': product['asin'],
            'title': product['title'][:50] + "...",
            'brand': product['brand'],
            'price': product['pricing'].get('current_price', 'N/A'),
            'rating': product['reviews'].get('average_rating', 'N/A'),
            'category': product['categories'][0] if product['categories'] else 'N/A',
            'fingerprint': product['fingerprint'][:8] + "..."
        })
    
    print("\n📊 PRODUCT SUMMARY:")
    for i, item in enumerate(summary, 1):
        print(f"   {i}. {item['title']}")
        print(f"      Brand: {item['brand']} | Price: {item['price']} | Rating: {item['rating']}")
        print(f"      Category: {item['category']} | Fingerprint: {item['fingerprint']}")
        print()


def demo_cross_platform_matching():
    """Demonstrate cross-platform matching scenario"""
    print("=" * 60)
    print("CROSS-PLATFORM MATCHING DEMO")
    print("=" * 60)
    
    # Parse Amazon product
    amazon_product = parse_amazon_product_enhanced("amazon_response.html")
    
    print("🛒 AMAZON PRODUCT ANALYSIS:")
    print(f"   Title: {amazon_product['title']}")
    print(f"   Brand: {amazon_product['brand']}")
    print(f"   Price: {amazon_product['pricing'].get('current_price', 'N/A')}")
    print()
    
    # Extract key matching features
    matching_features = {
        'brand': amazon_product['brand'],
        'model_number': amazon_product['matching_data'].get('model_number'),
        'barcode': amazon_product['matching_data'].get('barcode'),
        'title_keywords': amazon_product['matching_data'].get('title_keywords', []),
        'dimensions': amazon_product['physical_attributes'].get('dimensions'),
        'weight': amazon_product['physical_attributes'].get('weight'),
        'category': amazon_product['categories'][0] if amazon_product['categories'] else None
    }
    
    print("🔍 KEY MATCHING FEATURES FOR OTHER PLATFORMS:")
    for key, value in matching_features.items():
        if value:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    print()
    
    # Simulate matching with other platform data
    print("🔄 SIMULATED CROSS-PLATFORM MATCHING:")
    print("   1. Search by brand + model number")
    print("   2. Search by barcode (UPC/EAN)")
    print("   3. Fuzzy search by title keywords")
    print("   4. Filter by category and dimensions")
    print("   5. Compare physical attributes for final verification")
    print()


def demo_export_for_matching():
    """Demonstrate exporting data for external matching systems"""
    print("=" * 60)
    print("EXPORT FOR MATCHING DEMO")
    print("=" * 60)
    
    products = []
    html_files = ["amazon_response.html", "amazon_response1.html"]
    
    for html_file in html_files:
        product_data = parse_amazon_product_enhanced(html_file)
        
        # Create matching record
        matching_record = {
            'source': 'amazon',
            'asin': product_data['asin'],
            'title': product_data['title'],
            'brand': product_data['brand'],
            'model_number': product_data['matching_data'].get('model_number'),
            'barcode': product_data['matching_data'].get('barcode'),
            'price': product_data['pricing'].get('current_price'),
            'category': product_data['categories'][0] if product_data['categories'] else None,
            'keywords': product_data['matching_data'].get('title_keywords', []),
            'dimensions': product_data['physical_attributes'].get('dimensions'),
            'weight': product_data['physical_attributes'].get('weight'),
            'fingerprint': product_data['fingerprint'],
            'images': [img['url'] for img in product_data['images'][:3]],  # Top 3 images
            'rating': product_data['reviews'].get('average_rating'),
            'review_count': product_data['reviews'].get('total_reviews'),
            'specifications': product_data['specifications']
        }
        products.append(matching_record)
    
    # Export to JSON for matching system
    export_file = "products_for_matching.json"
    with open(export_file, 'w', encoding='utf-8') as file:
        json.dump(products, file, indent=2, ensure_ascii=False)
    
    print(f"📄 Exported {len(products)} products to {export_file}")
    print("   This file can be used with:")
    print("   • Database import systems")
    print("   • Machine learning matching algorithms")
    print("   • API-based product matching services")
    print("   • Cross-platform comparison tools")
    print()


def main():
    """Run all demo functions"""
    print("🚀 AMAZON PRODUCT PARSER - COMPREHENSIVE DEMO")
    print("This demo shows how to use the parser for cross-platform product matching")
    print()
    
    try:
        demo_basic_parsing()
        demo_detailed_extraction()
        demo_product_comparison()
        demo_batch_processing()
        demo_cross_platform_matching()
        demo_export_for_matching()
        
        print("✅ All demos completed successfully!")
        print()
        print("📚 NEXT STEPS:")
        print("1. Integrate with other e-commerce site parsers")
        print("2. Implement fuzzy matching algorithms")
        print("3. Set up automated product monitoring")
        print("4. Create product matching database")
        print("5. Build cross-platform price comparison system")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    main()
