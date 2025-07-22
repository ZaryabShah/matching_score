#!/usr/bin/env python3
"""
Debug Target JSON structure
"""

import json
import re
from one_prod_details.target_product_parser import TargetProductParser

def debug_target_json():
    """Debug the JSON structure to understand data layout."""
    
    # Read the Target HTML file
    try:
        with open("target_product_details.html", "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print("Error: target_product_details.html not found")
        return
    
    # Extract __NEXT_DATA__
    pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        print("❌ Could not find __NEXT_DATA__ script")
        return
    
    json_content = match.group(1)
    try:
        next_data = json.loads(json_content)
        print("✅ Successfully parsed __NEXT_DATA__ JSON")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return
    
    # Explore the structure
    print("\n🔍 Exploring JSON structure:")
    print(f"Top-level keys: {list(next_data.keys())}")
    
    if "props" in next_data:
        props = next_data["props"]
        print(f"Props keys: {list(props.keys())}")
        
        if "pageProps" in props:
            page_props = props["pageProps"]
            print(f"PageProps keys: {list(page_props.keys())}")
            
            # Check for __PRELOADED_QUERIES__
            if "__PRELOADED_QUERIES__" in page_props:
                queries = page_props["__PRELOADED_QUERIES__"]
                print(f"Preloaded queries structure: {type(queries)}")
                
                if isinstance(queries, dict) and "queries" in queries:
                    query_list = queries["queries"]
                    print(f"Found {len(query_list)} queries")
                    
                    # Examine each query
                    for i, query in enumerate(query_list):
                        if len(query) >= 2:
                            query_type = query[0] if len(query) > 0 else "unknown"
                            query_data = query[1] if len(query) > 1 else {}
                            
                            print(f"\nQuery {i+1}: {query_type}")
                            if isinstance(query_data, dict):
                                print(f"  Data keys: {list(query_data.keys())}")
                                
                                # Look for product data
                                if "data" in query_data:
                                    data = query_data["data"]
                                    print(f"  Data structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                                    
                                    if isinstance(data, dict) and "product" in data:
                                        product = data["product"]
                                        print(f"  ✅ Found product data!")
                                        print(f"  Product keys: {list(product.keys()) if isinstance(product, dict) else type(product)}")
                                        
                                        # Show some basic info
                                        if isinstance(product, dict):
                                            print(f"  TCIN: {product.get('tcin', 'N/A')}")
                                            if "item" in product:
                                                item = product["item"]
                                                if "product_description" in item:
                                                    desc = item["product_description"]
                                                    print(f"  Title: {desc.get('title', 'N/A')[:100]}...")
                                            if "price" in product:
                                                price = product["price"]
                                                print(f"  Price: {price.get('formatted_current_price', 'N/A')}")
    
    # Save structure for analysis
    structure_info = {
        "top_level_keys": list(next_data.keys()),
        "has_props": "props" in next_data,
        "has_page_props": "props" in next_data and "pageProps" in next_data["props"],
        "has_preloaded_queries": "props" in next_data and "pageProps" in next_data["props"] and "__PRELOADED_QUERIES__" in next_data["props"]["pageProps"]
    }
    
    with open("target_json_structure.json", "w") as f:
        json.dump(structure_info, f, indent=2)
    
    print(f"\n💾 Saved structure analysis to target_json_structure.json")

if __name__ == "__main__":
    debug_target_json()
