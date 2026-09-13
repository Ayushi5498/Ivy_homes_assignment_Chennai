# test_sqm_hypothesis.py
#
# Tests whether the 323 tiny-carpet magichomes records have carpet_area
# in square metres (sqm) rather than square feet (sqft).
# If true: carpet_area × 10.764 should be < super_built_up_area
# and form a believable ratio (carpet ~65-85% of SBA is normal in India).

import json
import statistics

SQM_TO_SQFT = 10.764

MIN_CARPET = {0: 0, 1: 200, 2: 350, 3: 550, 4: 750, 5: 950}
DEFAULT_MIN = 200

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

# Separate magichomes listings into "tiny carpet" vs "normal"
mag_tiny   = []
mag_normal = []

for r in listings:
    if r.get("website") != "magichomes": continue
    carpet  = r.get("carpet_area")
    bedroom = r.get("bedroom")
    pt      = r.get("property_type", "")
    if carpet is None or bedroom is None: continue
    if pt == "plot": continue
    min_c = MIN_CARPET.get(bedroom, DEFAULT_MIN)
    if bedroom > 0 and carpet < min_c:
        mag_tiny.append(r)
    else:
        mag_normal.append(r)

print(f"Magichomes tiny-carpet records  : {len(mag_tiny)}")
print(f"Magichomes normal-carpet records: {len(mag_normal)}")
print()


# ── 1. Test conversion hypothesis on the 323 tiny records ────────────────────

print("=" * 70)
print("PART 1 — carpet_area × 10.764 vs super_built_up_area (tiny records)")
print("=" * 70)

pass_count  = 0   # converted < SBA and ratio is plausible
fail_count  = 0
no_sba      = 0
ratios_pass = []

print(f"\n{'listing_id':<18} {'bed':>4} {'raw_c':>7} {'conv_c':>8} {'SBA':>8} "
      f"{'conv<SBA':>9} {'ratio%':>7}  verdict")
print(f"{'-'*18} {'-'*4} {'-'*7} {'-'*8} {'-'*8} {'-'*9} {'-'*7}  {'-'*10}")

for r in mag_tiny:
    lid    = r["listing_id"]
    carpet = r["carpet_area"]
    sba    = r.get("super_built_up_area")
    conv   = carpet * SQM_TO_SQFT
    bed    = r.get("bedroom")

    if sba is None or sba <= 0:
        no_sba += 1
        print(f"{lid:<18} {bed:>4} {carpet:>7} {conv:>8.1f} {'N/A':>8} "
              f"{'N/A':>9} {'N/A':>7}  no SBA data")
        continue

    ratio_pct = 100 * conv / sba
    conv_lt_sba = conv < sba
    # Plausible: carpet 55-90% of SBA is normal; outside = suspicious
    plausible = 55 <= ratio_pct <= 90

    if conv_lt_sba and plausible:
        verdict = "PASS ✓"
        pass_count += 1
        ratios_pass.append(ratio_pct)
    else:
        verdict = f"FAIL (ratio={ratio_pct:.0f}%)" if not plausible else "FAIL (conv>=SBA)"
        fail_count += 1

    print(f"{lid:<18} {bed:>4} {carpet:>7} {conv:>8.1f} {sba:>8} "
          f"{str(conv_lt_sba):>9} {ratio_pct:>7.1f}  {verdict}")

print(f"\n  PASS (conv < SBA and ratio 55-90%) : {pass_count}")
print(f"  FAIL                               : {fail_count}")
print(f"  No SBA data                        : {no_sba}")
if ratios_pass:
    print(f"  Avg ratio (passing records)        : {sum(ratios_pass)/len(ratios_pass):.1f}%")
    print(f"  Median ratio                       : {statistics.median(ratios_pass):.1f}%")


# ── 2. Are normal magichomes records already in sqft? ────────────────────────

print()
print("=" * 70)
print("PART 2 — Normal magichomes records: are carpet_area values in sqft?")
print("=" * 70)

normal_ratios = []
normal_pass = 0
normal_fail = 0

for r in mag_normal:
    carpet = r.get("carpet_area")
    sba    = r.get("super_built_up_area")
    if not carpet or not sba or sba <= 0: continue
    ratio_pct = 100 * carpet / sba
    # For sqft values, carpet should be 55-90% of SBA
    if 55 <= ratio_pct <= 90:
        normal_pass += 1
        normal_ratios.append(ratio_pct)
    else:
        normal_fail += 1

print(f"\n  Normal records with carpet 55-90% of SBA (looks like sqft) : {normal_pass}")
print(f"  Normal records outside 55-90% range                        : {normal_fail}")
if normal_ratios:
    print(f"  Avg ratio                                                   : {sum(normal_ratios)/len(normal_ratios):.1f}%")
    print(f"  Median ratio                                                : {statistics.median(normal_ratios):.1f}%")

# Sample 10 normal records to eyeball
print(f"\n  Sample 10 normal magichomes records (carpet vs SBA):")
print(f"  {'listing_id':<18} {'bed':>4} {'carpet':>8} {'SBA':>8} {'ratio%':>7}")
print(f"  {'-'*18} {'-'*4} {'-'*8} {'-'*8} {'-'*7}")
shown = 0
for r in mag_normal:
    if shown >= 10: break
    carpet = r.get("carpet_area"); sba = r.get("super_built_up_area")
    if not carpet or not sba: continue
    print(f"  {r['listing_id']:<18} {r.get('bedroom',''):>4} {carpet:>8} {sba:>8} "
          f"{100*carpet/sba:>7.1f}%")
    shown += 1


# ── 3. Cross-portal comparison: carpet/SBA ratios ────────────────────────────

print()
print("=" * 70)
print("PART 3 — Carpet/SBA ratio comparison across ALL portals")
print("(sanity check: all portals should show similar ratios if units consistent)")
print("=" * 70)

portal_ratios: dict[str, list] = {}
for r in listings:
    site   = r.get("website", "unknown")
    carpet = r.get("carpet_area")
    sba    = r.get("super_built_up_area")
    if not carpet or not sba or sba <= 0 or carpet <= 0: continue
    portal_ratios.setdefault(site, []).append(100 * carpet / sba)

print(f"\n  {'portal':<14} {'count':>6} {'median ratio%':>14} {'mean ratio%':>12}")
print(f"  {'-'*14} {'-'*6} {'-'*14} {'-'*12}")
for site, ratios in sorted(portal_ratios.items()):
    print(f"  {site:<14} {len(ratios):>6} {statistics.median(ratios):>14.1f} "
          f"{sum(ratios)/len(ratios):>12.1f}")
