import requests

url = "https://www.target.com/p/wicker-egg-chair-with-ottoman-egg-basket-lounge-chair-with-thick-cushion-comfy-egg-rattan-seat-for-indoor-outdoor-patio-porch-backyard/-/A-1001689724"

payload = ""
headers = {
    "cookie": "accessToken=eyJraWQiOiJlYXMyIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI2ZWUxMjQyMS05ODY4LTQwMGItOTllMC05NzY0MWUxNjY5YmEiLCJpc3MiOiJNSTYiLCJleHAiOjE3NTMyODAxODMsImlhdCI6MTc1MzE5Mzc4MywianRpIjoiVEdULjY0NDNkYjJlZDg5ZTQ0YzdiZjBjNGIyZDlhOGExMjEwLWwiLCJza3kiOiJlYXMyIiwic3V0IjoiRyIsImRpZCI6IjQzMTllY2RkZDBhNTMyYjZiYTE2YzhlMDc2MzFjNmFhZGM4MjQ5MmE0ZGFlODgzYjkzYmEyNTlhNDhiZDcxZTIiLCJzY28iOiJlY29tLm5vbmUsb3BlbmlkIiwiY2xpIjoiZWNvbS13ZWItMS4wLjAiLCJhc2wiOiJMIn0.Mo_jSuCoQpXRsoQ7itBjdLVTKWDY2HowPE_nR_cEtUDpw1M9fKhVPxy8wsqi2Hm-u9AcwwnccHOtXg5LnIju_sjswLSwRrpGhtuxX8CoGHicJrY72rtwOyx5oQ7g0vAbOH7ADKtXpqZxAIK4Aj4jLZg9YblZmcn8sk_zABHwz5bDUSST9CcOU2gEGFXDrWyFXbK834f08se9LrBOCs557CtOyahppE-gS45ephKi7APAga42-AI8_mGbsoRsvO92RWT5WfyLvVMeH_1Xujbgww5OVjBzvjccj67gvosBk3r6fNXk6TTdFRoiz2B6XwOIo7OBdodBK-7FVss-FCc2Lw; adScriptData=01; refreshToken=wSQQi59wtBCui6kW166Wo-0XivdxMw6Tch9_iE3z9pDAp6dV1e8FZAbO2L8UgpXhCg2h_9b5DzJmJfZvfFY_Ww; TealeafAkaSid=fA0Z1JuOq4v3EpvVw_FIAjl1IH7GI8MX; visitorId=0198327E21AD02009E7641FCDDB2771F; GuestLocation=40050%7C32.030%7C72.700%7CPB%7CPK; sapphire=1; idToken=eyJhbGciOiJub25lIn0.eyJzdWIiOiI2ZWUxMjQyMS05ODY4LTQwMGItOTllMC05NzY0MWUxNjY5YmEiLCJpc3MiOiJNSTYiLCJleHAiOjE3NTMyODAxODMsImlhdCI6MTc1MzE5Mzc4MywiYXNzIjoiTCIsInN1dCI6IkciLCJjbGkiOiJlY29tLXdlYi0xLjAuMCIsInBybyI6eyJmbiI6bnVsbCwiZm51IjpudWxsLCJlbSI6bnVsbCwicGgiOmZhbHNlLCJsZWQiOm51bGwsImx0eSI6ZmFsc2UsInN0IjoiMDEiLCJzbiI6bnVsbH19.; egsSessionId=2b90ed6f-6cc0-4120-b7ae-512073063d05",
    "^accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7^",
    "^accept-language": "en-US,en;q=0.9^",
    "^cache-control": "max-age=0^",
    "^device-memory": "8^",
    "^downlink": "10^",
    "^dpr": "1.5^",
    "^ect": "4g^",
    "^priority": "u=0, i^",
    "^rtt": "250^",
    "^sec-ch-device-memory": "8^",
    "^sec-ch-dpr": "1.5^",
    "^sec-ch-ua": "^\^Not",
    "Cookie": "^csm-sid=914-9361493-3807925; x-amz-captcha-1=1753048012390900; x-amz-captcha-2=NMEeDcMCIdStulUDaEttPQ==; session-id=132-5048832-5252361; session-id-time=2082787201l; i18n-prefs=USD; lc-main=en_US; skin=noskin; ubid-main=134-3385365-1946806; session-token=XO7GSKzisdIuyhpXzPWcHu6XfNIDZpTevMMWmTb9QbTo4fESt6QDpdtyN6CbUDOD+Yvy9zCWE5WfjjFPiS6nIyey3P8uukBB5FEKe7VIRDPJuqG5XupRUdAs/H6UPDzvxP2xO3guJWXYBPQZeckjk+m99ieDWR3sOQ98qJtatyaNw0nt4Ec6Hi0MsUrLNH4bCLyGOVmiSYkQ7ITkXzJf4ots/AUQf4WcGZ3Mu0JBmqcTtcdpsfAssi969h17N9hJd9+br4SThxqRzX5FsKyEku3HVD40yqt2WNbZW1IAubY1LW5JsctK1gv8SxPKJjw17EBqcx9q6CH89OoidaW9Q875dHS+K9qW; csm-hit=tb:PH5R76D5JJGMMY4HY4S7+s-6R2ZV1SGJ00S1DY6J59R^|1753100077660^&t:1753100077660^&adb:adblk_no; rxc=AMPob1+ITaV0WVPMZ5U^"
}

response = requests.request("GET", url, data=payload, headers=headers)

with open("target_product_details.html", "w", encoding="utf-8") as file:
    file.write(response.text)