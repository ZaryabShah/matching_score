import os
from datetime import datetime
from curl_cffi import requests

# Proxy configuration
proxy_url = "http://250621Ev04e-resi_region-US_California:5PjDM1IoS0JSr2c@ca.proxy-jet.io:1010"
proxies = {
    "http": proxy_url,
    "https": proxy_url
}

# Target URL
url = "https://www.amazon.com/s?k=chairs+living+room&crid=2UGBBSCCFLK5V&sprefix=chairs+living+room%2Caps%2C426&ref=nb_sb_noss_1"

# Headers configuration
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "device-memory": "8",
    "downlink": "1.4",
    "dpr": "1.5",
    "ect": "3g",
    "priority": "u=0, i",
    "rtt": "300",
    "sec-ch-device-memory": "8",
    "sec-ch-dpr": "1.5",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"10.0.0"',
    "sec-ch-viewport-width": "1280",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "viewport-width": "1280",
    "cookie": "csm-sid=914-9361493-3807925; x-amz-captcha-1=1753048012390900; x-amz-captcha-2=NMEeDcMCIdStulUDaEttPQ==; session-id=132-5048832-5252361; session-id-time=2082787201l; i18n-prefs=USD; lc-main=en_US; skin=noskin; ubid-main=134-3385365-1946806; session-token=i/AAXFcG1DGH38MqdJfJv6ri0S8N321KicL0yguouNfD0BOAn6bVlTwjItERn9jX7rMZSk0OAnB2mlSZImNOASzhRTA+lSjOfz7qelyhD1Y26wu4EckKBtF1iht3OC2hrkq9wX2eU7wcd1EVIHrgbLZGYe/+NMJxuAIwXcNs90zvTKnzZKc5ISKLbmcWRLq0tRj2coiI+EUPlEOr81a/WLnoxrWP+5eZj3Hj/CgZBvUKUGLDwgKb3I/4u/SB8zEYYDnjs+BaTLRzckU/Db/S+P2iruLsJOXlaRS5cloGw5lR05rgRaCQUYDYds92upj8LCxWM6RsVCDQv8B16NwWbTC/UKkQ8pXt; csm-hit=tb:AXJYQAC8NK0DP9EGGP47+s-AXJYQAC8NK0DP9EGGP47|1753041291657&t:1753041291657&adb:adblk_no; rxc=AMPob19TK6Z0WVPM4ZU"
}

def scrape_amazon():
    try:
        # Send request with rotating proxy and browser impersonation
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            impersonate="chrome120",
            timeout=30
        )
        
        # Check for successful response
        if response.status_code == 200:
            print(f"Success! Status code: {response.status_code}")
            return response.text
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.RequestsError as e:
        print(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def save_response(content):
    """Save response content to timestamped text file"""
    if not content:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"amazon_response_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Response saved to {filename}")
        return filename
    except IOError as e:
        print(f"Error saving file: {str(e)}")
        return None

if __name__ == "__main__":
    # Scrape Amazon and save response
    content = scrape_amazon()
    if content:
        save_response(content)
    else:
        print("Failed to retrieve content")