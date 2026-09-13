# inspect_project.py — deep dive into a single project_id
#
# HOW TO RUN:
#   python inspect_project.py

import json
import math
import requests

PROJECT_ID = "P40276"   # change this to inspect a different project

BASE_URL = "https://solve.ivy.homes"
API_KEY  = "IVY26-C5048846CD4F"

# ── Haversine helper ──────────────────────────────────────────────────────────
def haversine_m(lat1, lon1, lat2, lon2):
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# ── 1. Load listings and filter by project_id ─────────────────────────────────
with open("listings_all.json", encoding="utf-8") as f:
    all_listings = json.load(f)

matched = [r for r in all_listings if r.get("project_id") == PROJECT_ID]
print(f"Listings with project_id={PROJECT_ID}: {len(matched)}\n")

# ── 2. Print full details of up to 4 listings side by side ────────────────────
sample = matched[:4]

print("=" * 70)
print(f"FULL LISTING DETAILS — up to 4 listings for {PROJECT_ID}")
print("=" * 70)

# Collect all keys present across the sample
all_keys = []
seen = set()
for rec in sample:
    for k in rec.keys():
        if k not in seen:
            all_keys.append(k)
            seen.add(k)

# Print each field as a row across listings
col_w = 28
header = "Field".ljust(22) + "".join(f"Listing {i+1}".ljust(col_w) for i in range(len(sample)))
print(header)
print("-" * (22 + col_w * len(sample)))

for key in all_keys:
    row = key.ljust(22)
    for rec in sample:
        val = str(rec.get(key, "—"))
        # Truncate long values so columns stay readable
        if len(val) > col_w - 2:
            val = val[:col_w - 5] + "..."
        row += val.ljust(col_w)
    print(row)

# ── 3. Pairwise distances between the sampled listings ────────────────────────
print()
print("=" * 70)
print("PAIRWISE DISTANCES between the 4 sampled listings")
print("=" * 70)
for i in range(len(sample)):
    for j in range(i+1, len(sample)):
        r1, r2 = sample[i], sample[j]
        if r1.get("latitude") and r2.get("latitude"):
            d = haversine_m(r1["latitude"], r1["longitude"],
                            r2["latitude"], r2["longitude"])
            print(f"  Listing {i+1} ({r1.get('listing_id')}) ↔ "
                  f"Listing {j+1} ({r2.get('listing_id')}) : {d:,.1f} m")

# ── 4. Query GET /v1/projects/{project_id} directly ──────────────────────────
print()
print("=" * 70)
print(f"PROJECT RECORD — GET /v1/projects/{PROJECT_ID}")
print("=" * 70)

r = requests.post(f"{BASE_URL}/auth/login",
    json={"email": "demo1@ivy.homes", "password": "e478e79361"},
    headers={"X-API-Key": API_KEY})
token = r.json()["access_token"]
headers = {"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"}

resp = requests.get(f"{BASE_URL}/v1/projects/{PROJECT_ID}", headers=headers)
print(f"HTTP status: {resp.status_code}")
if resp.status_code == 200:
    proj = resp.json()
    for k, v in proj.items():
        print(f"  {k:<25} {v}")
else:
    print(resp.text)
