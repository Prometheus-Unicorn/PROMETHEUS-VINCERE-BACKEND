import os

keys = [k for k in os.environ if any(x in k.upper() for x in ["GOOGLE", "GEMINI", "FLOW", "VEO", "API", "TOKEN", "COOKIE"])]
for k in sorted(keys):
    val = os.environ[k]
    # mask
    masked = val[:6] + "..." + val[-4:] if len(val) > 12 else "***"
    print(f"{k}: {masked}")
