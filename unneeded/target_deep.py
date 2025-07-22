from curl_cffi import requests
import json

# Proxy configuration
proxy = "http://250621Ev04e-resi_region-US_California:5PjDM1IoS0JSr2c@ca.proxy-jet.io:1010"

# Request parameters
url = "https://redsky.target.com/redsky_aggregations/v1/web/product_summary_with_fulfillment_v1"
params = {
    "key": "9f36aeafbe60771e321a7cc95a78140772ab3e96",
    "tcins": "1001689725,84317924,93363636,1004165699,1004448663,1003149183,1004488126,87664302,88387728,1000691449,92687812,1000903515,1004421714,1000854058,1003724487,1003724525,1004852656,1001770975,1003724531,1003328451,1003411605,1002782051,1002221575,1000993536,1002221571,90305363,1000968208,1000993490,1004866750",
    "store_id": "2323",
    "zip": "20109",
    "state": "VA",
    "latitude": "38.800",
    "longitude": "-77.550",
    "scheduled_delivery_store_id": "1873",
    "paid_membership": "false",
    "base_membership": "false",
    "card_membership": "false",
    "required_store_id": "2323",
    "skip_price_promo": "true",
    "visitor_id": "0198299AFA95020180E21BC64E4076FC",
    "channel": "WEB",
    "page": "/s/chairs living room"
}

headers = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "cookie": "idToken=eyJhbGciOiJub25lIn0.eyJzdWIiOiI3MzI5ODMxNS1hODQwLTRjN2MtODI1OS1kN2FkYzgzZDIwMjgiLCJpc3MiOiJNSTYiLCJleHAiOjE3NTMxMzEwNzksImlhdCI6MTc1MzA0NDY3OSwiYXNzIjoiTCIsInN1dCI6IkciLCJjbGkiOiJlY29tLXdlYi0xLjAuMCIsInBybyI6eyJmbiI6bnVsbCwiZm51IjpudWxsLCJlbSI6bnVsbCwicGgiOmZhbHNlLCJsZWQiOm51bGwsImx0eSI6ZmFsc2UsInN0IjoiR0EiLCJzbiI6bnVsbH19.; refreshToken=67BrymoBTpafrExZ-6Kr8PW5e6yy60rxuTEJGUdGQKWS78ovax1BF_y08OWbzqpfpPHrM76nSDGnZY0KGKmKuQ; TealeafAkaSid=8D89D0yTmcZtpsrYdG45RA7ezFxdvNC5; sapphire=1; visitorId=0198299AFA95020180E21BC64E4076FC; adScriptData=GA; accessToken=eyJraWQiOiJlYXMyIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI3MzI5ODMxNS1hODQwLTRjN2MtODI1OS1kN2FkYzgzZDIwMjgiLCJpc3MiOiJNSTYiLCJleHAiOjE3NTMxMzEwNzksImlhdCI6MTc1MzA0NDY3OSwianRpIjoiVEdULjIwNTAxNWYyNTA4ODQ2Y2NiZmY1YzgyNTM5NjZmM2NjLWwiLCJza3kiOiJlYXMyIiwic3V0IjoiRyIsImRpZCI6IjJiMmE2YTRmZjUzNjAzYjhmMDY3NmIyZDQwNTU5YjcwODUzYjExYjQ1ZmE5ZGY1ZmNhZjAyNGI4ODA2M2I2NmMiLCJzY28iOiJlY29tLm5vbmUsb3BlbmlkIiwiY2xpIjoiZWNvbS13ZWItMS4wLjAiLCJhc2wiOiJMIn0.RWyyIr05LTYS5v5mPOOBuXu-tWv3LDtE9ompYj5B3w5uvMrZeBaWGNTsdb7cCUTlKxzQ2HiuqR3jJnPc4mQvmAtOQiIhgOLRlBGCvL92tWTe6i-7Rf-wHXrzEQbJmWlFNe_t0w1jPBGobhV8kLHh8ZFtpyIvAjUbIJIPceTOrNUkEoB2k81VeQucJPXfaY0erGjVP63eLMvIdNQjiZ1yjR5cs0Nzo9bj7g52g5JgLPGuxZz1NVm2ETq1UyN7SPBBrq7ldZ7Yf3DjsfRGAmh2Gqr79t5GFT1VqT3FOSanWDgArXQDJw3TG3QsBoUlXTiySCW2qirhyAnzIybC8SeLTw; egsSessionId=2d5bb13c-e9e0-49ce-9825-ee8af53c07b3; UserLocation=20109|38.800|-77.550|VA|US; _tgt_session=b8432ce6c432407e8bb276070c91a8f3.bef7b9acfe56f877cd770e3281b07011d058d4cffb948c49efe4ffe6628e303c57678ceece8a3ccbd9dc7f72770648ef3edc160a5362b8f9d6b5924864391721c68fd519540f1df942d6f99c94779b0650d82867785d3afaa13b89b5215a5be45a1b4ab0035a53dba28c0762416eae47585b43c7ab03c70bca90cb40561c486d806e2d2ff7852821f1c05fa97416addf6812a4ed91d066f3ed2584aafc2082f96a4859451da1981cfb9dd67657b666708f1999f6eab3f3d3f6fcb99c88c8f843029d82cfaa17a75caf9ec66aa6f6208aef9704c49f4ab2a35e1eb52d483677a991.0xa1e3d8500c8152559f65cfe6f3716c2f298fb8dab64db1d23e2b53bdd1c3761b; sddStore=DSI_1873|DSN_Gainesville|DSZ_20109; ffsession={%22sessionHash%22:%221b955515a277341753044685128%22,%22prevPageName%22:%22home page%22,%22prevPageType%22:%22home page%22,%22prevPageUrl%22:%22https://www.target.com/%22,%22sessionHit%22:1}; fiatsCookie=DSI_2323|DSN_Manassas West|DSZ_20109; ci_pixmgr=other",
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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

# Make the request using curl_cffi with Chrome impersonation
response = requests.get(
    url,
    params=params,
    headers=headers,
    proxy=proxy,
    impersonate="chrome110"
)

# Print response
print(f"Status Code: {response.status_code}")
with open("target_response.json", "w") as f:
    json.dump(response.json(), f, indent=4)