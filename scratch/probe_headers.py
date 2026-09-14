import urllib.request
import urllib.error

try:
    urllib.request.urlopen("http://127.0.0.1:9222/", timeout=3)
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    print("Headers:\n", e.headers)
except Exception as e:
    print("Err:", e)
