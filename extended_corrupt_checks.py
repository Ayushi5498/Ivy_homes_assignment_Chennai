# extended_corrupt_checks.py
#
# Runs two new corruption checks not caught by the original Q4 set:
#   CHECK 12 — carpet_area implausibly tiny for bedroom count
#   CHECK 13 — price/carpet_area below ₹500/sqft (unit entry error)
# Then recalculates Q6 with the expanded corrupt list.

import json, statistics

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

with open("submission.json", encoding="utf-8") as f:
    sub = json.load(f)

existing_corrupt = set(sub["answers"]["corrupt_listing_ids"])   # 45
existing_fake    = set(sub["answers"]["fake_listing_ids"])       # 93

print(f"Loaded {len(listings)} listings")
print(f"Existing corrupt IDs : {len(existing_corrupt)}")
print(f"Existing fake IDs    : {len(existing_fake)}\n")

by_id = {r["listing_id"]: r for r in listings}


# ── CHECK 12: carpet_area implausibly tiny for bedroom count ──────────────────
# Thresholds (sqft) — generous lower bounds for each bedroom count
# A 1BHK can realistically be ~250 sqft; 2BHK ~400 sqft; 3BHK ~600 sqft etc.
MIN_CARPET = {0: 0, 1: 200, 2: 350, 3: 550, 4: 750, 5: 950}
DEFAULT_MIN = 200   # for bedrooms not in the map (plots, studios)

c12 = {}
for r in listings:
    carpet  = r.get("carpet_area")
    bedroom = r.get("bedroom")
    pt      = r.get("property_type", "")
    if carpet is None or bedroom is None: continue
    if pt == "plot": continue   # plots don't have meaningful carpet area
    min_carpet = MIN_CARPET.get(bedroom, DEFAULT_MIN)
    if bedroom > 0 and carpet < min_carpet:
        c12[r["listing_id"]] = r

print("=" * 65)
print("CHECK 12 — carpet_area implausibly tiny for bedroom count")
print("=" * 65)
print(f"  Failed : {len(c12)} records\n")
print(f"  {'listing_id':<18} {'bed':>4} {'carpet':>8} {'min_expected':>13}  locality")
print(f"  {'-'*18} {'-'*4} {'-'*8} {'-'*13}  {'-'*15}")
for lid, r in sorted(c12.items()):
    bed = r.get("bedroom"); carpet = r.get("carpet_area")
    min_c = MIN_CARPET.get(bed, DEFAULT_MIN)
    print(f"  {lid:<18} {bed:>4} {carpet:>8} {min_c:>13}  {r.get('locality','')}")


# ── CHECK 13: price/carpet_area below ₹500/sqft ───────────────────────────────
PPSF_THRESHOLD = 500

c13 = {}
for r in listings:
    price  = r.get("price")
    carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0: continue
    if price / carpet < PPSF_THRESHOLD:
        c13[r["listing_id"]] = r

print(f"\n{'=' * 65}")
print("CHECK 13 — price/carpet_area below ₹500/sqft (unit entry error)")
print("=" * 65)
print(f"  Failed : {len(c13)} records\n")
print(f"  {'listing_id':<18} {'price':>12} {'carpet':>8} {'ppsf':>8}  locality")
print(f"  {'-'*18} {'-'*12} {'-'*8} {'-'*8}  {'-'*15}")
for lid, r in sorted(c13.items()):
    p = r.get("price"); c = r.get("carpet_area"); ppsf = p/c
    print(f"  {lid:<18} {p:>12,} {c:>8} {ppsf:>8.1f}  {r.get('locality','')}")


# ── Overlap analysis ──────────────────────────────────────────────────────────

new12 = set(c12.keys())
new13 = set(c13.keys())
all_new = new12 | new13

overlap_corrupt = all_new & existing_corrupt
overlap_fake    = all_new & existing_fake
overlap_12_13   = new12 & new13

print(f"\n{'=' * 65}")
print("OVERLAP ANALYSIS")
print("=" * 65)
print(f"  Check 12 unique IDs           : {len(new12)}")
print(f"  Check 13 unique IDs           : {len(new13)}")
print(f"  Check 12 ∩ Check 13           : {len(overlap_12_13)}  {sorted(overlap_12_13)}")
print(f"  New IDs (12 ∪ 13) total       : {len(all_new)}")
print(f"  Already in existing corrupt   : {len(overlap_corrupt)}  {sorted(overlap_corrupt)}")
print(f"  Already in existing fake      : {len(overlap_fake)}  {sorted(overlap_fake)}")
truly_new = all_new - existing_corrupt - existing_fake
print(f"  Truly new (not in either list): {len(truly_new)}")
print(f"  Truly new IDs: {sorted(truly_new)}")


# ── Combined corrupt list ─────────────────────────────────────────────────────

combined_corrupt = sorted(existing_corrupt | all_new)
print(f"\n{'=' * 65}")
print("COMBINED CORRUPT LIST (original 45 + new additions)")
print("=" * 65)
print(f"  Original corrupt : {len(existing_corrupt)}")
print(f"  New additions    : {len(truly_new)}")
print(f"  Combined total   : {len(combined_corrupt)}")
print(f"\n  Full sorted combined list:")
for lid in combined_corrupt:
    tag = " ← NEW" if lid in truly_new else ""
    print(f"    {lid}{tag}")


# ── Recalculate Q6 with updated exclusions ────────────────────────────────────

combined_corrupt_set = set(combined_corrupt)
exclude_all = combined_corrupt_set | existing_fake

ppsf_vals = []
skipped = 0
for r in listings:
    if r.get("is_live") is not True: continue
    if r.get("bedroom") != 2:        continue
    if r["listing_id"] in exclude_all: continue
    price  = r.get("price")
    carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0:
        skipped += 1
        continue
    ppsf_vals.append(price / carpet)

print(f"\n{'=' * 65}")
print("Q6 RECALCULATION — mean price/sqft, is_live=True, bedroom=2")
print(f"Excluding {len(combined_corrupt_set)} corrupt + {len(existing_fake)} fake IDs")
print("=" * 65)
print(f"  Records used     : {len(ppsf_vals)}")
print(f"  Skipped (no data): {skipped}")
print(f"  Min ppsf         : {min(ppsf_vals):.2f}")
print(f"  Max ppsf         : {max(ppsf_vals):.2f}")
print(f"  Mean ppsf        : {sum(ppsf_vals)/len(ppsf_vals):.2f}  ← Q6 ANSWER")
print(f"  Median ppsf      : {statistics.median(ppsf_vals):.2f}")

# Still any extreme outliers?
mean = sum(ppsf_vals) / len(ppsf_vals)
remaining_low  = [(v, lid) for r in listings
                  for lid, v in [(r["listing_id"], r.get("price",0)/r.get("carpet_area",1))]
                  if r.get("is_live") is True and r.get("bedroom")==2
                  and r["listing_id"] not in exclude_all
                  and r.get("price") and r.get("carpet_area")
                  and v < 500]
if remaining_low:
    print(f"\n  WARNING: {len(remaining_low)} records still below ₹500/sqft after filtering:")
    for v, lid in sorted(remaining_low):
        print(f"    {lid}  ppsf={v:.2f}")
else:
    print(f"\n  No remaining records below ₹500/sqft — clean dataset.")
