# confirm_sqm_correction.py
#
# After applying ×10.764 to both area fields of the 326 tiny-carpet records,
# checks whether the corrected values look like realistic properties.

import json, statistics

SQM_TO_SQFT = 10.764

MIN_CARPET = {0: 0, 1: 200, 2: 350, 3: 550, 4: 750, 5: 950}

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

# ── Separate tiny vs normal (same logic as before) ────────────────────────────
mag_tiny   = []
mag_normal = []
for r in listings:
    if r.get("website") != "magichomes": continue
    carpet  = r.get("carpet_area")
    bedroom = r.get("bedroom")
    pt      = r.get("property_type", "")
    if carpet is None or bedroom is None: continue
    if pt == "plot": continue
    min_c = MIN_CARPET.get(bedroom, MIN_CARPET.get(0, 200))
    if bedroom > 0 and carpet < min_c:
        mag_tiny.append(r)
    else:
        mag_normal.append(r)

# ── Reference: normal 2BHK ppsf across all portals ───────────────────────────
ref_ppsf = []
for r in listings:
    if r.get("bedroom") != 2: continue
    price = r.get("price"); carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0: continue
    # Skip known-tiny MAG records to get a clean reference
    if r in mag_tiny: continue
    ppsf = price / carpet
    if 3000 <= ppsf <= 20000:   # sanity-bounded reference range
        ref_ppsf.append(ppsf)

ref_median = statistics.median(ref_ppsf)
ref_mean   = sum(ref_ppsf) / len(ref_ppsf)
print(f"Reference 2BHK ppsf (normal listings): median={ref_median:.0f}  mean={ref_mean:.0f}  n={len(ref_ppsf)}\n")

# ── Apply correction and evaluate ─────────────────────────────────────────────
corrected_2bhk = []
corrected_all  = []

for r in mag_tiny:
    raw_carpet = r.get("carpet_area")
    raw_sba    = r.get("super_built_up_area")
    price      = r.get("price")
    if not raw_carpet or not price: continue

    conv_carpet = raw_carpet * SQM_TO_SQFT
    conv_sba    = raw_sba * SQM_TO_SQFT if raw_sba else None
    ppsf_corrected = price / conv_carpet

    entry = {
        "listing_id"   : r["listing_id"],
        "bedroom"      : r.get("bedroom"),
        "locality"     : r.get("locality"),
        "raw_carpet"   : raw_carpet,
        "raw_sba"      : raw_sba,
        "conv_carpet"  : conv_carpet,
        "conv_sba"     : conv_sba,
        "price"        : price,
        "ppsf_raw"     : price / raw_carpet,
        "ppsf_corrected": ppsf_corrected,
        "carpet_sane"  : 300 <= conv_carpet <= 3000,   # broad sanity range for any bedroom
        "ppsf_sane"    : 3000 <= ppsf_corrected <= 20000,
    }
    corrected_all.append(entry)
    if r.get("bedroom") == 2:
        corrected_2bhk.append(entry)

# Summary
n_carpet_sane = sum(1 for e in corrected_all if e["carpet_sane"])
n_ppsf_sane   = sum(1 for e in corrected_all if e["ppsf_sane"])
n_both_sane   = sum(1 for e in corrected_all if e["carpet_sane"] and e["ppsf_sane"])

print("=" * 70)
print(f"CORRECTION SANITY SUMMARY (all {len(corrected_all)} tiny records)")
print("=" * 70)
print(f"  Corrected carpet in sensible range (300-3000 sqft) : {n_carpet_sane} / {len(corrected_all)}")
print(f"  Corrected ppsf in sensible range (₹3000-20000/sqft): {n_ppsf_sane} / {len(corrected_all)}")
print(f"  BOTH sane                                          : {n_both_sane} / {len(corrected_all)}")

# ── 5 corrected 2BHK examples ─────────────────────────────────────────────────
print()
print("=" * 70)
print("5 CORRECTED 2BHK EXAMPLES")
print("=" * 70)
print(f"\n  {'listing_id':<18} {'locality':<14} {'price':>12} "
      f"{'raw_c':>7} {'conv_c':>8} {'conv_sba':>9} "
      f"{'ppsf_raw':>10} {'ppsf_conv':>10}  sane?")
print(f"  {'-'*18} {'-'*14} {'-'*12} "
      f"{'-'*7} {'-'*8} {'-'*9} "
      f"{'-'*10} {'-'*10}  {'-'*5}")

for e in corrected_2bhk[:5]:
    sane = "✓" if e["carpet_sane"] and e["ppsf_sane"] else "✗"
    print(f"  {e['listing_id']:<18} {str(e['locality']):<14} {e['price']:>12,} "
          f"{e['raw_carpet']:>7} {e['conv_carpet']:>8.0f} {e['conv_sba'] if e['conv_sba'] else 0:>9.0f} "
          f"{e['ppsf_raw']:>10.0f} {e['ppsf_corrected']:>10.0f}  {sane}")

# ── Compare corrected ppsf to reference ───────────────────────────────────────
if corrected_2bhk:
    conv_ppsf_vals = [e["ppsf_corrected"] for e in corrected_2bhk if e["ppsf_sane"]]
    print(f"\n  Reference 2BHK ppsf median : {ref_median:,.0f} ₹/sqft")
    if conv_ppsf_vals:
        print(f"  Corrected 2BHK ppsf median : {statistics.median(conv_ppsf_vals):,.0f} ₹/sqft")
        print(f"  Corrected 2BHK ppsf mean   : {sum(conv_ppsf_vals)/len(conv_ppsf_vals):,.0f} ₹/sqft")
        print(f"  ({len(conv_ppsf_vals)} of {len(corrected_2bhk)} 2BHK records have sane corrected ppsf)")

# ── What does this mean for Q6? ───────────────────────────────────────────────
print()
print("=" * 70)
print("Q6 IMPACT: recalculate mean ppsf INCLUDING corrected 2BHK records")
print("=" * 70)

with open("submission.json", encoding="utf-8") as f:
    sub = json.load(f)

# Current corrupt set (45 original)
original_corrupt = set(sub["answers"]["corrupt_listing_ids"])
fake_ids         = set(sub["answers"]["fake_listing_ids"])

# Tiny MAG ids
tiny_ids = {r["listing_id"] for r in mag_tiny}

# Scenario A: exclude tiny as corrupt (current approach) → 375 excluded
excl_A = original_corrupt | fake_ids
# Scenario B: correct tiny records and include them → only 45+93 excluded
excl_B = original_corrupt | fake_ids   # same, but we use corrected area

ppsf_A, ppsf_B = [], []
for r in listings:
    if r.get("is_live") is not True: continue
    if r.get("bedroom") != 2:        continue
    price = r.get("price"); carpet = r.get("carpet_area")
    if not price or not carpet or carpet <= 0: continue
    lid = r["listing_id"]

    # Scenario A — current: exclude tiny MAG as corrupt
    # (we need the combined 376 here — original 45 + 331 new from extended check)
    # For now compare: original 45+93 vs original 45+93+tiny_ids
    if lid not in (original_corrupt | fake_ids | tiny_ids):
        ppsf_A.append(price / carpet)

    # Scenario B — corrected: use converted carpet for tiny MAG
    if lid in tiny_ids:
        corrected_c = carpet * SQM_TO_SQFT
        ppsf_B.append(price / corrected_c)
    elif lid not in (original_corrupt | fake_ids):
        ppsf_B.append(price / carpet)

print(f"\n  Scenario A — exclude tiny MAG as corrupt:")
print(f"    Records : {len(ppsf_A)}")
print(f"    Mean    : {sum(ppsf_A)/len(ppsf_A):.2f} ₹/sqft")

print(f"\n  Scenario B — correct tiny MAG areas and include:")
print(f"    Records : {len(ppsf_B)}")
print(f"    Mean    : {sum(ppsf_B)/len(ppsf_B):.2f} ₹/sqft")
