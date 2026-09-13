# calc_avg_price_per_sqft.py
#
# HOW TO RUN:
#   python calc_avg_price_per_sqft.py
#
# Calculates mean price/carpet_area for is_live=True, bedroom=2 listings,
# excluding corrupt and fake listing IDs from submission.json.

import json

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

with open("submission.json", encoding="utf-8") as f:
    submission = json.load(f)

# Build exclusion set
exclude_ids = set(submission["answers"]["corrupt_listing_ids"]) | \
              set(submission["answers"]["fake_listing_ids"])

print(f"Total listings loaded        : {len(listings)}")
print(f"IDs to exclude (corrupt+fake): {len(exclude_ids)}")

# Apply filters
filtered = []
skipped_no_carpet = 0

for r in listings:
    if r.get("is_live") is not True:       continue   # must be live
    if r.get("bedroom") != 2:              continue   # must be 2-bedroom
    if r["listing_id"] in exclude_ids:     continue   # exclude corrupt/fake

    price  = r.get("price")
    carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0:
        skipped_no_carpet += 1
        continue

    filtered.append(price / carpet)

print(f"Skipped (missing price/area) : {skipped_no_carpet}")
print(f"Records used for calculation : {len(filtered)}")
print()

if filtered:
    mean_ppsf = sum(filtered) / len(filtered)
    print(f"Mean price/carpet_area  : {mean_ppsf:.2f}  ← ANSWER")
    print(f"Min  price/carpet_area  : {min(filtered):.2f}")
    print(f"Max  price/carpet_area  : {max(filtered):.2f}")

    # Quick outlier check: how many are > 3x or < 0.3x the mean
    high = sum(1 for v in filtered if v > mean_ppsf * 3)
    low  = sum(1 for v in filtered if v < mean_ppsf * 0.3)
    print(f"\nSanity: values > 3× mean ({mean_ppsf*3:.0f}) : {high}")
    print(f"Sanity: values < 0.3× mean ({mean_ppsf*0.3:.0f})  : {low}")
