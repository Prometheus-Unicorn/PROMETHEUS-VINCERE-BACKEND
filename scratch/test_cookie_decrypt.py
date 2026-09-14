import os
import sqlite3
import shutil
import json
import base64
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

USER_DATA = r"C:\Users\HomePC\AppData\Local\Google\Chrome\User Data"
LOCAL_STATE_PATH = os.path.join(USER_DATA, "Local State")
COOKIE_DB_PATH = os.path.join(USER_DATA, "Profile 12", "Network", "Cookies")

def get_secret_key():
    with open(LOCAL_STATE_PATH, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:] # Remove 'DPAPI' prefix
    secret_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return secret_key

def decrypt_cookie_val(encrypted_val, key):
    try:
        if encrypted_val[:3] == b'v10':
            nonce = encrypted_val[3:15]
            ciphertext = encrypted_val[15:]
            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode('utf-8', errors='ignore')
        else:
            return win32crypt.CryptUnprotectData(encrypted_val, None, None, None, 0)[1].decode('utf-8', errors='ignore')
    except Exception as e:
        return f"ERR:{e}"

def test_extract():
    temp_db = "scratch/temp_cookies.db"
    os.makedirs("scratch", exist_ok=True)
    try:
        shutil.copyfile(COOKIE_DB_PATH, temp_db)
        print("Copied cookie DB successfully!")
    except Exception as e:
        print("Copy failed:", e)
        return

    try:
        key = get_secret_key()
        print(f"Obtained DPAPI key ({len(key)} bytes).")
    except Exception as e:
        print("DPAPI key failed:", e)
        return

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, path, is_secure, is_httponly, expires_utc, encrypted_value FROM cookies WHERE host_key LIKE '%google.com%'")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} Google cookies in Profile 12 DB.")

    success_count = 0
    flow_cookies = []
    for host, name, path, is_secure, is_httponly, expires_utc, enc_val in rows:
        val = decrypt_cookie_val(enc_val, key)
        if not val.startswith("ERR:"):
            success_count += 1
            flow_cookies.append({
                "name": name,
                "value": val,
                "domain": host,
                "path": path,
                "secure": bool(is_secure),
                "httpOnly": bool(is_httponly),
            })
            if name in ["SID", "__Secure-1PSID", "__Secure-1PSIDTS", "OSID"]:
                print(f"  [SUCCESS] {name} ({host}): {val[:25]}...")

    print(f"\nDecryption summary: {success_count}/{len(rows)} cookies decrypted successfully!")

    if success_count > 0:
        out_path = "config/flow_auth_fresh.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"cookies": flow_cookies, "origins": []}, f, indent=2)
        print(f"Saved {len(flow_cookies)} fresh decrypted cookies to {out_path}!")

if __name__ == "__main__":
    test_extract()
