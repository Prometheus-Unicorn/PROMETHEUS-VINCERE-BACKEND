import urllib.request
import urllib.error

urls = [
    "http://127.0.0.1:9222/",
    "http://127.0.0.1:9222/json",
    "http://127.0.0.1:9222/json/list",
    "http://127.0.0.1:9222/json/version",
    "http://127.0.0.1:9222/json/protocol",
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"{u} -> {resp.status}: {resp.read().decode('utf-8')[:100]}")
    except urllib.error.HTTPError as e:
        print(f"{u} -> HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')[:100]}")
    except Exception as e:
        print(f"{u} -> ERR: {e}")
