#!/usr/bin/env python3
"""Fetch MOT history from the DVSA MOT History API and write mot-history.json.

Privacy: the registration number is read from a secret and stripped from the
output — it never appears in the committed JSON or the rendered page.

Required environment (GitHub repo secrets):
  DVSA_CLIENT_ID, DVSA_CLIENT_SECRET, DVSA_TOKEN_URL, DVSA_SCOPE, DVSA_API_KEY,
  VEHICLE_REG
Exits 0 without writing anything if credentials are absent (pre-approval state).
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date

REQUIRED = ["DVSA_CLIENT_ID", "DVSA_CLIENT_SECRET", "DVSA_TOKEN_URL", "DVSA_SCOPE", "DVSA_API_KEY", "VEHICLE_REG"]
env = {k: os.environ.get(k, "").strip() for k in REQUIRED}
missing = [k for k, v in env.items() if not v]
if missing:
    print(f"DVSA credentials not configured ({', '.join(missing)}) — leaving sample data in place.")
    sys.exit(0)

# 1. OAuth2 client-credentials token (Microsoft Entra)
token_body = urllib.parse.urlencode({
    "grant_type": "client_credentials",
    "client_id": env["DVSA_CLIENT_ID"],
    "client_secret": env["DVSA_CLIENT_SECRET"],
    "scope": env["DVSA_SCOPE"],
}).encode()
req = urllib.request.Request(env["DVSA_TOKEN_URL"], data=token_body,
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
with urllib.request.urlopen(req, timeout=30) as r:
    token = json.load(r)["access_token"]

# 2. MOT history for the vehicle
reg = urllib.parse.quote(env["VEHICLE_REG"].replace(" ", ""))
api = urllib.request.Request(
    f"https://history.mot.api.gov.uk/v1/trade/vehicles/registration/{reg}",
    headers={"Authorization": f"Bearer {token}", "X-API-Key": env["DVSA_API_KEY"], "Accept": "application/json"},
)
with urllib.request.urlopen(api, timeout=30) as r:
    data = json.load(r)

# 3. Redact identity, mark live, write
data.pop("registration", None)
data.pop("vin", None)
out = {"sample": False, "generated": date.today().isoformat(), **data}
with open("mot-history.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"Wrote mot-history.json with {len(out.get('motTests', []))} tests (registration redacted).")
