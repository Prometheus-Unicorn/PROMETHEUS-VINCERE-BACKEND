import os

path = r"C:\Users\HomePC\AppData\Local\Google\Chrome\User Data\Profile 12\Network\Cookies"
try:
    with open(path, "rb") as f:
        data = f.read(100)
        print("Success! Read 100 bytes from Cookies file.")
except Exception as e:
    print("Failed to open Cookies:", type(e), e)
