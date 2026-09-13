# check_is_live.py
#
# HOW TO RUN:
#   python check_is_live.py

import json

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

live    = [r for r in listings if r.get("is_live") is True]
not_live = [r for r in listings if r.get("is_live") is False]
missing  = [r for r in listings if "is_live" not in r]

total = len(listings)
check = len(live) + len(not_live) + len(missing)

print(f"Total records          : {total}")
print(f"  is_live = True       : {len(live)}")
print(f"  is_live = False      : {len(not_live)}")
print(f"  is_live missing      : {len(missing)}")
print(f"  Sum (sanity check)   : {check}  {'✓ matches' if check == total else '✗ MISMATCH'}")

if not_live:
    print(f"\nExample listing_ids with is_live=False (up to 3):")
    for rec in not_live[:3]:
        print(f"  {rec.get('listing_id')}")
