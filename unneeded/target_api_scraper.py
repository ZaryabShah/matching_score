#!/usr/bin/env python3
"""
Target Redsky API Response Scraper
Captures product data from Target's API and saves to JSON
"""

import json
import time
import tls_client
from urllib.parse import urlencode

class TargetAPIScraper:
    def __init__(self):
        # Create TLS session with Chrome fingerprint
        self.session = tls_client.Session(
            client_identifier="chrome_133_psk",
            random_tls_extension_order=True
        )
        
        # User agent from your HAR data
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        
        # Base API endpoint
        self.base_url = "https://redsky.target.com/redsky_aggregations/v1/web/product_summary_with_fulfillment_v1"
        
        print("✅ Target API Scraper initialized with Chrome TLS fingerprint")
    
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def build_api_url(self, tcins, store_id=2323, zip_code="20109", state="VA", 
                     latitude=38.800, longitude=-77.550, scheduled_delivery_store_id=1873):
        """Build the Target API URL with parameters"""
        
        # Convert TCIN list to comma-separated string if it's a list
        if isinstance(tcins, list):
            tcins_str = ",".join(str(tcin) for tcin in tcins)
        else:
            tcins_str = str(tcins)
        
        # API parameters from your HAR data
        params = {
            "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
            "tcins": tcins_str,
            "store_id": store_id,
            "zip": zip_code,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
            "scheduled_delivery_store_id": scheduled_delivery_store_id,
            "paid_membership": "false",
            "base_membership": "false", 
            "card_membership": "false",
            "required_store_id": store_id,
            "skip_price_promo": "true",
            "visitor_id": "0198299AFA95020180E21BC64E4076FC",
            "channel": "WEB",
            "page": "/s/chairs+living+room"
        }
        
        return f"{self.base_url}?{urlencode(params)}"

    def fetch_product_data(self, tcins, output_file="target_response.json"):
        """Fetch product data from Target API and save to JSON"""
        
        self.log(f"🔍 Fetching data for TCINs: {tcins}")
        
        # Build the API URL
        api_url = self.build_api_url(tcins)
        self.log(f"🌐 API URL: {api_url[:100]}...")
        
        # Headers from your HAR data
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "origin": "https://www.target.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://www.target.com/s?searchTerm=chairs+living+room",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": self.user_agent
        }
        
        # Add cookies from your HAR data (optional - may work without them)
        cookies = {
            "idToken": "eyJhbGciOiJub25lIn0.eyJzdWIiOiI3MzI5ODMxNS1hODQwLTRjN2MtODI1OS1kN2FkYzgzZDIwMjgiLCJpc3MiOiJNSTYiLCJleHAiOjE3NTMxMzEwNzksImlhdCI6MTc1MzA0NDY3OSwiYXNzIjoiTCIsInN1dCI6IkciLCJjbGkiOiJlY29tLXdlYi0xLjAuMCIsInBybyI6eyJmbiI6bnVsbCwiZm51IjpudWxsLCJlbSI6bnVsbCwicGgiOmZhbHNlLCJsZWQiOm51bGwsImx0eSI6ZmFsc2UsInN0IjoiR0EiLCJzbiI6bnVsbH19.",
            "visitorId": "0198299AFA95020180E21BC64E4076FC",
            "sapphire": "1"
        }
        
        try:
            # Make the API request
            response = self.session.get(
                api_url,
                headers=headers,
                cookies=cookies
            )
            
            self.log(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse JSON response
                try:
                    response_data = response.json()
                    self.log(f"✅ Successfully parsed JSON response")
                    self.log(f"📊 Response contains {len(str(response_data))} characters")
                    
                    # Save to JSON file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(response_data, f, indent=2, ensure_ascii=False)
                    
                    self.log(f"💾 Response saved to {output_file}")
                    
                    # Print summary of data
                    if isinstance(response_data, dict):
                        self.log(f"🔍 Response keys: {list(response_data.keys())}")
                        
                        # Look for product data
                        if 'data' in response_data:
                            data = response_data['data']
                            if 'product_summaries' in data:
                                products = data['product_summaries']
                                self.log(f"🛍️ Found {len(products)} products")
                                
                                # Show first product info
                                if products:
                                    first_product = products[0]
                                    if 'tcin' in first_product:
                                        self.log(f"📦 First product TCIN: {first_product['tcin']}")
                                    if 'item' in first_product and 'product_description' in first_product['item']:
                                        title = first_product['item']['product_description'].get('title', 'No title')
                                        self.log(f"📝 First product: {title[:50]}...")
                    
                    return response_data
                    
                except json.JSONDecodeError as e:
                    self.log(f"❌ Failed to parse JSON: {e}", "ERROR")
                    # Save raw response for debugging
                    with open(f"target_raw_response.txt", 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    self.log(f"💾 Raw response saved to target_raw_response.txt")
                    return None
                    
            else:
                self.log(f"❌ API request failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:300]}...")
                return None
                
        except Exception as e:
            self.log(f"❌ Request error: {e}", "ERROR")
            return None

    def fetch_chairs_data(self):
        """Fetch the specific chair data from your HAR example"""
        
        # TCINs from your HAR data
        chair_tcins = [
            "1001689725", "84317924", "93363636", "1004165699", "1004448663",
            "1003149183", "1004488126", "87664302", "88387728", "1000691449",
            "92687812", "1000903515", "1004421714", "1000854058", "1003724487",
            "1003724525", "1004852656", "1001770975", "1003724531", "1003328451",
            "1003411605", "1002782051", "1002221575", "1000993536", "1002221571",
            "90305363", "1000968208", "1000993490", "1004866750"
        ]
        
        self.log(f"🪑 Fetching chair data for {len(chair_tcins)} products")
        return self.fetch_product_data(chair_tcins, "target_chairs_response.json")

def main():
    print("=" * 60)
    print("🎯 Target Redsky API Scraper")
    print("📡 Fetching product data and saving to JSON")
    print("=" * 60)
    
    scraper = TargetAPIScraper()
    
    # Fetch the chair data from your example
    result = scraper.fetch_chairs_data()
    
    if result:
        print("=" * 60)
        print("✅ SUCCESS: Target API data scraped and saved!")
        print("📄 Check target_chairs_response.json for the full data")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ FAILED: Could not fetch Target API data")
        print("🔍 Check logs for details")
        print("=" * 60)

if __name__ == "__main__":
    main()
