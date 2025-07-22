#!/usr/bin/env python3
"""
Test script to verify enhanced parsing capabilities
"""
import json
from enhanced_amazon_parser import EnhancedAmazonProductParser

def test_enhanced_parsing():
    """Test the enhanced parser with existing HTML files"""
    parser = EnhancedAmazonProductParser()
    
    # Test files
    test_files = [
        "amazon_response.html",
        "amazon_response1.html"
    ]
    
    for file_name in test_files:
        try:
            print(f"\n{'='*60}")
            print(f"Testing with: {file_name}")
            print(f"{'='*60}")
            
            # Parse the HTML file
            with open(file_name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract comprehensive product data
            product_data = parser.parse(html_content)
            
            print(f"\nProduct Title: {product_data.get('title', 'N/A')}")
            print(f"Brand: {product_data.get('brand', 'N/A')}")
            print(f"ASIN: {product_data.get('asin', 'N/A')}")
            
            # Show comprehensive specifications
            specs = product_data.get('specifications', {})
            print(f"\nComprehensive Specifications ({len(specs)} items):")
            for key, value in specs.items():
                print(f"  {key}: {value}")
            
            # Show physical attributes
            physical = product_data.get('physical_attributes', {})
            print(f"\nPhysical Attributes:")
            for key, value in physical.items():
                print(f"  {key}: {value}")
            
            # Show product identifiers
            identifiers = product_data.get('product_identifiers', {})
            print(f"\nProduct Identifiers:")
            for key, value in identifiers.items():
                print(f"  {key}: {value}")
            
            # Save detailed output to file
            output_file = f"test_results_{file_name.replace('.html', '.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(product_data, f, indent=2, ensure_ascii=False)
            
            print(f"\nDetailed output saved to: {output_file}")
            
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
    
    print(f"\n{'='*60}")
    print("Testing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_enhanced_parsing()
