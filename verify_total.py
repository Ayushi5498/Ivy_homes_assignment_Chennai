# verify_total.py
#
# HOW TO RUN:
#   python verify_total.py
#
# Checks whether the "total" reported by GET /v1/listings matches
# the number of records saved in listings_all.json.

import json
import requests

BASE_URL = "https://solve.ivy.homes"
EMAIL    = "demo1@ivy.homes"
PASSWORD = "e478e79361"
API_KEY  = "IVY26-C5048846CD4F"

# ── 1. Login ──────────────────────────────────────────────────────────────────
r = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
    headers={"X-API-Key": API_KEY}
)
r.raise_for_status()
token = r.json()["access_token"]

headers = {
    "X-API-Key":     API_KEY,
    "Authorization": f"Bearer {token}",
}

# ── 2. Single request to /v1/listings — read "total" field ───────────────────
resp = requests.get(
    f"{BASE_URL}/v1/listings",
    headers=headers,
    params={"offset": 0, "limit": 50}   # limit=50 (API cap); we only need "total"
)
resp.raise_for_status()
api_total = resp.json()["total"]
print(f"API reported total  : {api_total}")

# ── 3. Count records in listings_all.json ────────────────────────────────────
with open("listings_all.json", "r", encoding="utf-8") as f:
    saved = json.load(f)
saved_count = len(saved)
print(f"Records in JSON file: {saved_count}")

# ── 4. Compare ────────────────────────────────────────────────────────────────
print()
if api_total == saved_count:
    print(f"MATCH: API total = {api_total}, saved records = {saved_count}")
else:
    print(f"MISMATCH: API total = {api_total}, saved records = {saved_count} "
          f"— investigate before trusting this data")
