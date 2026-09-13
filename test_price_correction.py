# test_price_correction.py
#
# Tests whether the 6 new price-error records (ppsf < 500, not in original 45)
# look realistic after multiplying price by 100 (lakhs → rupees).

import json, statistics

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

with open("submission.json", encoding="utf-8") as f:
    sub = json.load(f)

original_corrupt = set(sub["answers"]["corrupt_listing_ids"])

# The 6 new price-error IDs (from Check 13, not already in original 45)
NEW_PRICE_ERROR_IDS = {
    "100-4001484", "100-4001961", "DWE-4000745",
    "MAG-4000870", "MAG-4001467", "MAG-4002092",
    "SQU-4001342", "ZER-4002683"
}
# Filter to only truly new ones (not in original 45)
truly_new_price_errors = NEW_PRICE_ERROR_IDS - original_corrupt
print(f"Truly new price-error IDs (not in original 45): {len(truly_new_price_errors)}")
print(f"  {sorted(truly_new_price_errors)}\n")

# Reference ppsf from clean dataset
ref_ppsf = []
for r in listings:
    if r["listing_id"] in original_corrupt: continue
    price = r.get("price"); carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0: continue
    ppsf = price / carpet
    if 3000 <= ppsf <= 25000:
        ref_ppsf.append(ppsf)

ref_median = statistics.median(ref_ppsf)
ref_mean   = sum(ref_ppsf) / len(ref_ppsf)
print(f"Reference dataset ppsf  median={ref_median:,.0f}  mean={ref_mean:,.0f}  n={len(ref_ppsf)}\n")

# Show all 6 records
by_id = {r["listing_id"]: r for r in listings}

print("=" * 80)
print("6 NEW PRICE-ERROR RECORDS — raw vs ×100 corrected")
print("=" * 80)
print(f"\n  {'listing_id':<18} {'bed':>4} {'locality':<14} {'carpet':>8} "
      f"{'raw_price':>14} {'ppsf_raw':>10} "
      f"{'corr_price':>14} {'ppsf_corr':>10}  in_range?")
print(f"  {'-'*18} {'-'*4} {'-'*14} {'-'*8} "
      f"{'-'*14} {'-'*10} "
      f"{'-'*14} {'-'*10}  {'-'*9}")

for lid in sorted(truly_new_price_errors):
    r = by_id[lid]
    price  = r.get("price")
    carpet = r.get("carpet_area")
    bed    = r.get("bedroom")
    loc    = r.get("locality", "")

    ppsf_raw  = price / carpet
    corr_price = price * 100
    ppsf_corr  = corr_price / carpet

    in_range = "✓" if ref_median * 0.5 <= ppsf_corr <= ref_median * 2.0 else "✗"

    print(f"  {lid:<18} {bed:>4} {str(loc):<14} {carpet:>8} "
          f"{price:>14,} {ppsf_raw:>10.1f} "
          f"{corr_price:>14,} {ppsf_corr:>10.0f}  {in_range}")

print(f"\n  Reference median ppsf : {ref_median:,.0f} ₹/sqft")
print(f"  Acceptable range      : {ref_median*0.5:,.0f} – {ref_median*2.0:,.0f} ₹/sqft")
