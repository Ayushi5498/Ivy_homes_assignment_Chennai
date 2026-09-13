# calc_q6_final.py — final Q6 calculation with unit corrections applied

import json, statistics

SQM_TO_SQFT = 10.764
MIN_CARPET = {0: 0, 1: 200, 2: 350, 3: 550, 4: 750, 5: 950}

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)
with open("submission.json", encoding="utf-8") as f:
    sub = json.load(f)

corrupt_ids = set(sub["answers"]["corrupt_listing_ids"])   # 45
fake_ids    = set(sub["answers"]["fake_listing_ids"])       # 93
exclude_ids = corrupt_ids | fake_ids

# Identify the 326 sqm-area MAG records
sqm_ids = set()
for r in listings:
    if r.get("website") != "magichomes": continue
    carpet  = r.get("carpet_area")
    bedroom = r.get("bedroom")
    pt      = r.get("property_type", "")
    if carpet is None or bedroom is None or pt == "plot": continue
    if bedroom > 0 and carpet < MIN_CARPET.get(bedroom, 200):
        sqm_ids.add(r["listing_id"])

# Identify the 8 price-in-thousands records
price_k_ids = {
    "100-4001484", "100-4001961", "DWE-4000745", "MAG-4000870",
    "MAG-4001467", "MAG-4002092", "SQU-4001342", "ZER-4002683"
}

print(f"sqm-area records identified  : {len(sqm_ids)}")
print(f"price-×1000 records          : {len(price_k_ids)}")
print(f"Excluded (corrupt + fake)    : {len(exclude_ids)}")
print()

ppsf_vals = []
skipped = 0

for r in listings:
    if r.get("is_live") is not True: continue
    if r.get("bedroom") != 2:        continue
    lid = r["listing_id"]
    if lid in exclude_ids:           continue

    price  = r.get("price")
    carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0:
        skipped += 1
        continue

    # Apply corrections where needed
    if lid in sqm_ids:
        carpet = carpet * SQM_TO_SQFT      # convert sqm → sqft
    if lid in price_k_ids:
        price = price * 1000               # convert thousands → full rupees

    ppsf_vals.append(price / carpet)

print(f"Records used in Q6 calculation : {len(ppsf_vals)}")
print(f"  of which sqm-corrected (2BHK): {sum(1 for r in listings if r['listing_id'] in sqm_ids and r.get('bedroom')==2 and r.get('is_live') and r['listing_id'] not in exclude_ids)}")
print(f"  of which price-corrected      : {sum(1 for r in listings if r['listing_id'] in price_k_ids and r.get('bedroom')==2 and r.get('is_live') and r['listing_id'] not in exclude_ids)}")
print(f"Skipped (missing data)          : {skipped}")
print()

mean_ppsf   = sum(ppsf_vals) / len(ppsf_vals)
median_ppsf = statistics.median(ppsf_vals)
print(f"Mean   price/carpet_area : {mean_ppsf:.2f}  ← Q6 ANSWER")
print(f"Median price/carpet_area : {median_ppsf:.2f}")
print(f"Min                      : {min(ppsf_vals):.2f}")
print(f"Max                      : {max(ppsf_vals):.2f}")
