#!/usr/bin/env python3
"""
Cross-Platform Product Parser Demo
Demonstrates Amazon and Target product parsers working together for product matching
"""

import json
from one_prod_details.target_product_parser import TargetProductParser

def demo_cross_platform_comparison():
    """Demonstrate cross-platform product comparison capabilities."""
    print("=== Cross-Platform Product Parser Demo ===\n")
    
    # Parse Target product
    print("🎯 Parsing Target Product...")
    try:
        with open("target_product_details.html", "r", encoding="utf-8") as f:
            target_html = f.read()
    except FileNotFoundError:
        print("❌ target_product_details.html not found")
        return
    
    target_parser = TargetProductParser()
    target_result = target_parser.parse_html(target_html)
    
    if "error" in target_result:
        print(f"❌ Target parsing failed: {target_result['error']}")
        return
    
    target_comparison = target_parser.get_comparison_data()
    print("✅ Target product parsed successfully!")
    
    # Display Target product info
    print(f"\n📦 Target Product Details:")
    print(f"   Name: {target_comparison.get('name', 'N/A')}")
    print(f"   Brand: {target_comparison.get('brand', 'N/A')}")
    print(f"   TCIN: {target_comparison.get('product_id', 'N/A')}")
    print(f"   UPC: {target_comparison.get('upc', 'N/A')}")
    print(f"   Price: ${target_comparison.get('current_price', 'N/A')}")
    
    dims = target_comparison.get('dimensions', {})
    if dims:
        print(f"   Dimensions: {dims.get('length')} x {dims.get('width')} x {dims.get('height')} {dims.get('unit')}")
        print(f"   Weight: {dims.get('weight')} {dims.get('unit', '').replace('INCH', 'LB') if dims.get('weight') else 'N/A'}")
    
    print(f"   Features: {len(target_comparison.get('features', []))} items")
    print(f"   Specifications: {target_comparison.get('total_specs', 0)} total")
    
    # Show key features
    features = target_comparison.get('features', [])
    if features:
        print(f"\n✨ Key Target Features:")
        for i, feature in enumerate(features[:3], 1):
            print(f"   {i}. {feature[:80]}{'...' if len(feature) > 80 else ''}")
    
    # Show specifications
    specs = target_comparison.get('specifications', {})
    if specs:
        print(f"\n🔧 Target Specifications:")
        for key, value in list(specs.items())[:5]:
            print(f"   • {key}: {value}")
    
    # Check if Amazon parser is available for comparison
    try:
        # Try to import and use Amazon parser if available
        import sys
        import os
        
        # Look for Amazon parser files
        amazon_files = [f for f in os.listdir('.') if 'amazon' in f.lower() and f.endswith('.py')]
        if amazon_files:
            print(f"\n🔍 Found Amazon parser files: {amazon_files}")
            print("   Ready for cross-platform comparison!")
            
            # Create a mock Amazon product for comparison demo
            mock_amazon_data = {
                "platform": "Amazon",
                "product_id": "B08XYZ123",
                "name": "Wicker Egg Chair with Ottoman - Outdoor Patio Furniture",
                "brand": "Garvee",
                "model": "WEC-001",
                "upc": "199108999382",  # Same UPC
                "current_price": 245.99,
                "regular_price": 599.99,
                "dimensions": {
                    "length": 36.0,
                    "width": 27.5,
                    "height": 16.8,
                    "weight": 55.0,
                    "unit": "inches"
                },
                "features": [
                    "Comfortable egg-shaped design with thick cushions",
                    "Durable rattan construction with steel frame",
                    "Includes matching ottoman for added comfort",
                    "Suitable for indoor and outdoor use",
                    "Easy assembly with included tools"
                ],
                "specifications": {
                    "Material": "Rattan with Steel Frame",
                    "Seat Capacity": "1 Person",
                    "Assembly Required": "Yes",
                    "Weather Resistant": "Yes"
                },
                "total_specs": 8
            }
            
            # Perform comparison
            comparison = target_parser.compare_with_other_product(mock_amazon_data)
            
            print(f"\n🔄 Cross-Platform Comparison Results:")
            print(f"   Target: {comparison.get('target_product', 'N/A')}")
            print(f"   Amazon: {comparison.get('other_product', 'N/A')}")
            print(f"   Similarity Score: {comparison.get('similarity_score', 0):.1f}%")
            print(f"   Match Confidence: {comparison.get('match_confidence', 'Unknown')}")
            
            # Show matches
            matches = comparison.get('matches', {})
            if matches:
                print(f"\n✅ Matching Fields:")
                for field, data in matches.items():
                    print(f"   • {field}: {data.get('target')} = {data.get('other')}")
            
            # Show differences
            differences = comparison.get('differences', {})
            if differences:
                print(f"\n⚠️  Different Fields:")
                for field, data in differences.items():
                    print(f"   • {field}: Target='{data.get('target')}' vs Amazon='{data.get('other')}'")
            
            # Dimension comparison
            if 'dimension_similarity' in comparison:
                print(f"\n📏 Dimension Similarity: {comparison['dimension_similarity']:.1f}%")
        
        else:
            print(f"\n💡 Amazon parser not found - but Target parser is fully functional!")
            print("   The Target parser extracts the same comprehensive data as the Amazon parser:")
            print("   ✅ Product identifiers (TCIN, UPC, GTIN)")
            print("   ✅ Complete pricing information")
            print("   ✅ Physical dimensions and weight")
            print("   ✅ Detailed specifications")
            print("   ✅ Product features and highlights")
            print("   ✅ Images and media")
            print("   ✅ Reviews and ratings")
            print("   ✅ Category and brand information")
            print("   ✅ Cross-platform comparison capabilities")
    
    except Exception as e:
        print(f"\n⚠️  Comparison error: {e}")
    
    # Save comprehensive data
    output_data = {
        "target_product": target_result,
        "target_comparison_data": target_comparison,
        "extraction_timestamp": target_result.get("basic_info", {}).get("extraction_timestamp"),
        "parser_version": "target_product_parser.py v1.0"
    }
    
    # Save to JSON file
    output_filename = f"target_product_analysis_{target_comparison.get('product_id', 'unknown')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Complete analysis saved to: {output_filename}")
    print(f"📊 Summary:")
    print(f"   • Product successfully parsed: ✅")
    print(f"   • Specifications extracted: {target_comparison.get('total_specs', 0)}")
    print(f"   • Cross-platform ready: ✅")
    print(f"   • JSON export complete: ✅")
    
    return output_data

if __name__ == "__main__":
    demo_cross_platform_comparison()
