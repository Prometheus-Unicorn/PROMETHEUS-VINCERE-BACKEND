import json
import os
from pathlib import Path

raw_cookies = [
  {"domain":".google.com","expirationDate":1823887200.196806,"hostOnly":False,"httpOnly":False,"name":"SID","path":"/","sameSite":"unspecified","secure":False,"session":False,"storeId":"0","value":"g.a000Cgkeeyu9A4LYLohM7utABCwWXAWrwaG79_meky6--3VBY7bxb0kgwyBfZ_ankgd9VUBrYAACgYKAa4SARASFQHGX2MiH73ks5qiHQ1CS8EefN4NShoVAUF8yKoavhhVUJiTBdWD0apNpm_s0076"},
  {"domain":".google.com","expirationDate":1823887200.196893,"hostOnly":False,"httpOnly":True,"name":"__Secure-1PSID","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"g.a000Cgkeeyu9A4LYLohM7utABCwWXAWrwaG79_meky6--3VBY7bxCeUBkyX2Lh2-TMaHTs0J_gACgYKAbQSARASFQHGX2Mix9x8vYb9MJ_Z445xMXAeKRoVAUF8yKouemiWL9XCiaeTfML1dOj30076"},
  {"domain":".google.com","expirationDate":1823887200.196966,"hostOnly":False,"httpOnly":True,"name":"__Secure-3PSID","path":"/","sameSite":"no_restriction","secure":True,"session":False,"storeId":"0","value":"g.a000Cgkeeyu9A4LYLohM7utABCwWXAWrwaG79_meky6--3VBY7bxKv7oDJqK_Yn98cE-Y9bdDgACgYKASUSARASFQHGX2MiCwXlV25oXozxY8qGbIlhGRoVAUF8yKpRoB72RB85TEaCMa0LwM-60076"},
  {"domain":".google.com","expirationDate":1823887200.197229,"hostOnly":False,"httpOnly":True,"name":"HSID","path":"/","sameSite":"unspecified","secure":False,"session":False,"storeId":"0","value":"ASOIVYarSm2ntlIDH"},
  {"domain":".google.com","expirationDate":1823887200.197298,"hostOnly":False,"httpOnly":True,"name":"SSID","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"Ackx47lh_oSD9w1_s"},
  {"domain":".google.com","expirationDate":1823887200.197373,"hostOnly":False,"httpOnly":False,"name":"APISID","path":"/","sameSite":"unspecified","secure":False,"session":False,"storeId":"0","value":"PigRrrhLrEY42NHY/AWLkWW1-voTEFUtcJ"},
  {"domain":".google.com","expirationDate":1823887200.197445,"hostOnly":False,"httpOnly":False,"name":"SAPISID","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"SDOqn5YcAOnvNN-H/AS_4dVQ60-vWegDot"},
  {"domain":".google.com","expirationDate":1823887200.197511,"hostOnly":False,"httpOnly":False,"name":"__Secure-1PAPISID","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"SDOqn5YcAOnvNN-H/AS_4dVQ60-vWegDot"},
  {"domain":".google.com","expirationDate":1823887200.197743,"hostOnly":False,"httpOnly":False,"name":"__Secure-3PAPISID","path":"/","sameSite":"no_restriction","secure":True,"session":False,"storeId":"0","value":"SDOqn5YcAOnvNN-H/AS_4dVQ60-vWegDot"},
  {"domain":"flow.google.com","expirationDate":1823887220.066911,"hostOnly":True,"httpOnly":True,"name":"OSID","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"g.a000Cgkee1kI7M0dk1cfFIpH4TPNaLgVaJ20dFGlev4AojpUWQFjZ2PNOvOUyQb3Xkh60I-ZHwACgYKAT8SARASFQHGX2MiG02lLJ4Z2MlprO8YbaXmMxoVAUF8yKrC8T4fccN2wPrHa2BIYXpk0076"},
  {"domain":"flow.google.com","expirationDate":1823887220.067316,"hostOnly":True,"httpOnly":True,"name":"__Secure-OSID","path":"/","sameSite":"no_restriction","secure":True,"session":False,"storeId":"0","value":"g.a000Cgkee1kI7M0dk1cfFIpH4TPNaLgVaJ20dFGlev4AojpUWQFj5WlKleuKgJmr0a4U62w1rwACgYKATgSARASFQHGX2MiHbh9Csno5oJquP4kx9UQAhoVAUF8yKoFsMGyJ_UFyvEEAb6Q2PFk0076"},
  {"domain":".flow.google.com","expirationDate":1823894929.861186,"hostOnly":False,"httpOnly":False,"name":"_ga","path":"/","sameSite":"unspecified","secure":False,"session":False,"storeId":"0","value":"GA1.1.1055454996.1789327224"},
  {"domain":".google.com","expirationDate":1804879283.287272,"hostOnly":False,"httpOnly":False,"name":"SEARCH_SAMESITE","path":"/","sameSite":"strict","secure":False,"session":False,"storeId":"0","value":"CgQI5aEB"},
  {"domain":".google.com","expirationDate":1804879283.287484,"hostOnly":False,"httpOnly":True,"name":"AEC","path":"/","sameSite":"lax","secure":True,"session":False,"storeId":"0","value":"AdJVEavoTpYaIUIgu6QOfe_-Skbb7HcgD1huY1peUXXZ9nf4Hd9DY4TnWdw"},
  {"domain":".google.com","expirationDate":1805138162.076431,"hostOnly":False,"httpOnly":True,"name":"NID","path":"/","sameSite":"no_restriction","secure":True,"session":False,"storeId":"0","value":"534=AA6DRL9IctPHjxNnVDgfnqfHsrgr5JCl343u9-mL9XWP1-IvNcRDEAtTcFAbLq2L_QjeXXnffcF11QUDW-yP5Tv6XVhxrkEkuRlQyyL92HmPsJdqUEn-llgekDVAG_rXfYk0PsJrRmzb1PJIs59yR-4bXc1TXqLa3zfbtqTT0ySAs8ZROduTTUyRshwPOi6mV-_ubbgYG_0gPoN76keRGqTbpSPuyaPfaWtW8i05--gbpiPIf5LrUE3aM9aamn82vvjrQ-7_Hc-8g16SH2EeBk1ogvPjjgAX2s_y4PRM2gJ2wmtwdeNbe2DYQIb414kogARabsY_qGIYshkHY5ZC3ixZtECwr5h0oveqCrjmbbA26LxaH_5kBA5gwugbK2sVxnWH"},
  {"domain":".flow.google.com","expirationDate":1823894929.938016,"hostOnly":False,"httpOnly":False,"name":"_ga_X2GNH8R5NS","path":"/","sameSite":"unspecified","secure":False,"session":False,"storeId":"0","value":"GS2.1.s1789334929$o2$g1$t1789334929$j60$l0$h1515964225"},
  {"domain":".google.com","expirationDate":1823513666.086464,"hostOnly":False,"httpOnly":True,"name":"__Secure-ENID","path":"/","sameSite":"lax","secure":True,"session":False,"storeId":"0","value":"CtgCCAISigIBAQxeRY4TEhlJQXJTv_DsIjkt1uGhoXw2mgN2mgSs2geVCyWzXFNt4EUHHiZNF2BogafbHOQyv8mPi9icB-R_LkKlvPRFHnEAjFMmCfabxmCzBGGooJkk_Mdedqzn0eyC-Uz4JJ-rgLKDC37IEAEda03JG8ykQ75yskjhCxTXrz8vHfoyGiDqdnDHFItE2_79pqFKGvufa6h3yY3H4qkxXAKVaHxxPkdqOZpjtOeyfI23_T_BlBb-cfKBA1OnW0ETXQqD9uvqujhfFNDCju6QYrhSUxYdaC1605p3X0Vd652P2IVOWeD9iiX8Sm06Q7SSQ_WHAwsrT75gXFNbOtjOjLGoIxrE4bRjhCgCMkUBfWzEqn8tD9AmG6OAF5BJT6gOnnhEc_aMkQvQ4L2hc8L88rz2fzdCiX7cikGrLVphLBCo7VAYoURowqbiJs9E8JiD2AI"},
  {"domain":".google.com","expirationDate":1820870938.961833,"hostOnly":False,"httpOnly":True,"name":"__Secure-1PSIDTS","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"sidts-CjEBXMw41RTKaoBkqBg4L0j3AUDF0W_Xddyk2ybg4ynXQzAtL61f2XX_PpisMJSM40e1EAA"},
  {"domain":".google.com","expirationDate":1820870938.962393,"hostOnly":False,"httpOnly":True,"name":"__Secure-3PSIDTS","path":"/","sameSite":"no_restriction","secure":True,"session":False,"storeId":"0","value":"sidts-CjEBXMw41RTKaoBkqBg4L0j3AUDF0W_Xddyk2ybg4ynXQzAtL61f2XX_PpisMJSM40e1EAA"},
  {"domain":".google.com","expirationDate":1820870968.346918,"hostOnly":False,"httpOnly":False,"name":"SIDCC","path":"/","sameSite":"unspecified","secure":False,"session":False,"storeId":"0","value":"AKEyXzWWcxjceGgaCnCt9tiJk3mSMltAcmegrhg0_AlbkoPBZHcAgFWjt0LhVZztZOei_TKc5w"},
  {"domain":".google.com","expirationDate":1820870968.347319,"hostOnly":False,"httpOnly":True,"name":"__Secure-1PSIDCC","path":"/","sameSite":"unspecified","secure":True,"session":False,"storeId":"0","value":"AKEyXzU_yPdNZNKjZK1gII4Ign4V3njFhZf3zPrEwxAFiy63H-8kGDrREeoyAuwJijMAetl1Tg"},
  {"domain":".google.com","expirationDate":1820870968.348056,"hostOnly":False,"httpOnly":True,"name":"__Secure-3PSIDCC","path":"/","sameSite":"no_restriction","secure":True,"session":False,"storeId":"0","value":"AKEyXzV7kWYCWW3PK-bRj_76ZEWlD2hvlffHPvjm_IDzpGgvftPyPrlfOujFbWnpc8lxaaJlSA"}
]

playwright_cookies = []
for c in raw_cookies:
    pc = {
        "name": c["name"],
        "value": c["value"],
        "domain": c["domain"],
        "path": c.get("path", "/"),
        "secure": c.get("secure", False),
        "httpOnly": c.get("httpOnly", False),
    }
    if "expirationDate" in c:
        pc["expires"] = float(c["expirationDate"])
    ss = str(c.get("sameSite", "")).lower()
    if ss == "no_restriction":
        pc["sameSite"] = "None"
    elif ss == "lax":
        pc["sameSite"] = "Lax"
    elif ss == "strict":
        pc["sameSite"] = "Strict"
    else:
        # Default or unspecified: if secure, None or Lax
        pc["sameSite"] = "Lax"

    playwright_cookies.append(pc)

out_path = Path("config/flow_auth.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
storage_state = {
    "cookies": playwright_cookies,
    "origins": []
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(storage_state, f, indent=2)

print(f"Saved {len(playwright_cookies)} Playwright cookies to {out_path}")
