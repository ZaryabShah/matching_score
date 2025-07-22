#!/usr/bin/env python3
"""
Test script for the Product Matching System
Tests individual components and the complete workflow
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_amazon_fetcher():
    """Test Amazon product fetching with a known ASIN"""
    print("🧪 Testing Amazon Product Fetcher...")
    
    try:
        from amazon_complete_fetcher_parser import AmazonProductExtractor
        
        # Test with the existing ASIN from your sample data
        test_asin = "B00FS3VJAO"
        
        extractor = AmazonProductExtractor()
        result = extractor.extract_product(test_asin)
        
        if 'error' in result:
            print(f"❌ Amazon fetch failed: {result['error']}")
            return False
        
        print(f"✅ Amazon product fetched: {result.get('title', 'Unknown')[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Amazon fetcher test failed: {str(e)}")
        return False

def test_target_fetcher():
    """Test Target product fetching with a known URL"""
    print("\n🧪 Testing Target Product Fetcher...")
    
    try:
        from target_complete_fetcher_parser import TargetProductExtractor
        
        # Test with existing Target URL from your sample data
        test_url = "https://www.target.com/p/wicker-egg-chair-with-ottoman-egg-basket-lounge-chair-with-thick-cushion-comfy-egg-rattan-seat-for-indoor-outdoor-patio-porch-backyard/-/A-1001689724"
        
        extractor = TargetProductExtractor()
        result = extractor.extract_product(test_url)
        
        if 'error' in result:
            print(f"❌ Target fetch failed: {result['error']}")
            return False
        
        product_name = result.get('basic_info', {}).get('name', 'Unknown')
        print(f"✅ Target product fetched: {product_name[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Target fetcher test failed: {str(e)}")
        return False

def test_scoring_system():
    """Test the scoring system with sample data"""
    print("\n🧪 Testing Scoring System...")
    
    try:
        from product_matching_system import ProductMatchingScorer
        
        # Create sample product data
        amazon_sample = {
            'title': 'Home Office Chair Ergonomic Desk Chair Mesh Computer Chair',
            'brand': 'BestOffice',
            'pricing': {'current_price': '38.97'},
            'specifications': {
                'model_number': 'BO-001',
                'upc': '123456789012'
            }
        }
        
        target_sample = {
            'basic_info': {
                'name': 'Home Office Chair Ergonomic Desk Chair',
                'brand': 'BestOffice',
                'upc': '123456789012',
                'model_number': 'BO-001'
            },
            'pricing': {
                'formatted_current_price': '$39.99'
            }
        }
        
        scorer = ProductMatchingScorer()
        score, breakdown = scorer.calculate_match_score(amazon_sample, target_sample)
        
        print(f"✅ Scoring test completed. Score: {score:.1f}")
        print(f"   Score breakdown: {breakdown}")
        
        return score > 0
        
    except Exception as e:
        print(f"❌ Scoring system test failed: {str(e)}")
        return False

def test_search_modules():
    """Test availability of search modules"""
    print("\n🧪 Testing Search Module Availability...")
    
    amazon_search = False
    target_search = False
    
    try:
        from unneeded.realtime_amazon_extractor import RealTimeAmazonExtractor
        amazon_search = True
        print("✅ Amazon search module available")
    except ImportError:
        print("⚠️  Amazon search module not available")
    
    try:
        from unneeded.dynamic_target_scraper import TargetScraper
        target_search = True
        print("✅ Target search module available")
    except ImportError:
        print("⚠️  Target search module not available")
    
    return amazon_search, target_search

def test_complete_workflow():
    """Test the complete workflow with existing data"""
    print("\n🧪 Testing Complete Workflow (Simulation)...")
    
    try:
        from product_matching_system import ProductMatchingSystem
        
        # Initialize system
        system = ProductMatchingSystem()
        
        # Load existing sample data for testing
        amazon_file = Path("amazon_product_B00FS3VJAO_1753197529.json")
        target_file = Path("target_product_1001689724_1753202927.json")
        
        if not amazon_file.exists() or not target_file.exists():
            print("⚠️  Sample data files not found. Skipping workflow test.")
            return False
        
        # Load sample data
        with open(amazon_file, 'r') as f:
            amazon_data = json.load(f)
        
        with open(target_file, 'r') as f:
            target_data = json.load(f)
        
        # Test scoring
        scorer = system.scorer
        score, breakdown = scorer.calculate_match_score(amazon_data, target_data)
        
        print(f"✅ Workflow simulation completed")
        print(f"   Sample comparison score: {score:.1f}")
        print(f"   Confidence: {scorer.get_confidence_level(score)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Product Matching System - Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test individual components
    tests = [
        ("Amazon Fetcher", test_amazon_fetcher),
        ("Target Fetcher", test_target_fetcher),
        ("Scoring System", test_scoring_system),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    for test_name, test_func in tests:
        total_tests += 1
        if test_func():
            tests_passed += 1
    
    # Test module availability
    print("\n" + "=" * 50)
    amazon_search, target_search = test_search_modules()
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        
    # Print usage instructions
    print(f"\n📖 Usage Instructions:")
    print(f"   Basic usage: python product_matching_system.py \"office chair\"")
    print(f"   With options: python product_matching_system.py \"gaming chair\" --max-results 10")
    print(f"   Interactive: python product_matching_system.py")
    
    if not amazon_search:
        print(f"\n⚠️  Note: Amazon search not available. You can still use with specific ASINs.")
    if not target_search:
        print(f"⚠️  Note: Target search not available. You can still use with specific URLs.")

if __name__ == "__main__":
    main()
