import curl_cffi.requests as requests  # Use curl_cffi for browser-like TLS

url = "https://www.amazon.com/dp/B00FS3VJAO/"
querystring = {"th": "1"}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "device-memory": "8",
    "downlink": "10",
    "dpr": "1.5",
    "ect": "4g",
    "priority": "u=0, i",
    "rtt": "250",
    "sec-ch-device-memory": "8",
    "sec-ch-dpr": "1.5",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "cookie": "csm-sid=914-9361493-3807925; x-amz-captcha-1=1753048012390900; x-amz-captcha-2=NMEeDcMCIdStulUDaEttPQ==; session-id=132-5048832-5252361; session-id-time=2082787201l; i18n-prefs=USD; lc-main=en_US; skin=noskin; ubid-main=134-3385365-1946806; session-token=XO7GSKzisdIuyhpXzPWcHu6XfNIDZpTevMMWmTb9QbTo4fESt6QDpdtyN6CbUDOD+Yvy9zCWE5WfjjFPiS6nIyey3P8uukBB5FEKe7VIRDPJuqG5XupRUdAs/H6UPDzvxP2xO3guJWXYBPQZeckjk+m99ieDWR3sOQ98qJtatyaNw0nt4Ec6Hi0MsUrLNH4bCLyGOVmiSYkQ7ITkXzJf4ots/AUQf4WcGZ3Mu0JBmqcTtcdpsfAssi969h17N9hJd9+br4SThxqRzX5FsKyEku3HVD40yqt2WNbZW1IAubY1LW5JsctK1gv8SxPKJjw17EBqcx9q6CH89OoidaW9Q875dHS+K9qW; csm-hit=tb:PH5R76D5JJGMMY4HY4S7+s-6R2ZV1SGJ00S1DY6J59R|1753100077660&t:1753100077660&adb:adblk_no; rxc=AMPob1+ITaV0WVPMZ5U"
}

response = requests.get(
    url,
    params=querystring,
    headers=headers,
    impersonate="chrome120"  # Mimics Chrome 120 browser
)

with open("amazon_response.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("Response saved to amazon_response.html")