# extract_final_ids.py — prints the final ID lists for submission.json

import json, statistics
from collections import defaultdict

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

CORRUPT_IDS = {
    "100-4000397","100-4000449","100-4000457","100-4000491","100-4000545",
    "100-4000738","100-4001530","100-4001703","100-4002961","DWE-4000236",
    "DWE-4000307","DWE-4000412","DWE-4000824","DWE-4001368","DWE-4001410",
    "DWE-4001424","DWE-4001442","DWE-4002105","DWE-4002247","DWE-4002374",
    "DWE-4002712","DWE-4002806","DWE-4003067","MAG-4000145","MAG-4000283",
    "MAG-4000675","MAG-4001981","MAG-4002776","MAG-4003100","SQU-4000308",
    "SQU-4000459","SQU-4000583","SQU-4001225","SQU-4002391","SQU-4002483",
    "SQU-4002544","ZER-4000021","ZER-4001161","ZER-4001287","ZER-4001669",
    "ZER-4001686","ZER-4001726","ZER-4002091","ZER-4002305","ZER-4002352"
}
clean = [r for r in listings if r["listing_id"] not in CORRUPT_IDS]

# Contact index
contact_to_ids = defaultdict(list)
for r in clean:
    c = (r.get("posted_by_contact") or "").strip()
    if c:
        contact_to_ids[c].append(r["listing_id"])

a15 = {lid for c, ids in contact_to_ids.items() if len(ids) >= 15 for lid in ids}

# Check C (40-70% band, ppsf >= 100)
group_ppsf = defaultdict(list)
for r in clean:
    price = r.get("price"); carpet = r.get("carpet_area")
    loc = (r.get("locality") or "").strip().lower()
    bed = r.get("bedroom")
    if not price or not carpet or carpet <= 0 or not loc or bed is None: continue
    ppsf = price / carpet
    if ppsf < 100: continue
    group_ppsf[(loc, bed)].append((ppsf, r["listing_id"]))

check_c = set()
for (loc, bed), entries in group_ppsf.items():
    if len(entries) < 5: continue
    med = statistics.median(p for p, _ in entries)
    for ppsf, lid in entries:
        if med * 0.40 <= ppsf <= med * 0.70:
            check_c.add(lid)

fake_93 = sorted(a15 & check_c)

# Extreme price errors (ppsf < 100)
price_error_ids = []
for r in clean:
    price = r.get("price"); carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0: continue
    if price / carpet < 100:
        price_error_ids.append(r["listing_id"])
price_error_ids.sort()

print("FAKE_LISTING_IDS (93):")
print(json.dumps(fake_93, indent=2))
print(f"\nTotal: {len(fake_93)}")

print("\nPRICE_ERROR_IDS (extreme ppsf < 100):")
print(json.dumps(price_error_ids, indent=2))
print(f"\nTotal: {len(price_error_ids)}")
