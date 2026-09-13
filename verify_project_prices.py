# verify_project_prices.py
#
# 1. Full distribution of raw price_max values across all 460 projects
# 2. Detailed boundary zone (5-15) to check for ambiguity
# 3. Cross-check corrected price_max vs price_min (must have max >= min)
# 4. Compare corrected prices to actual listing prices in same locality

import json, statistics
from collections import defaultdict

with open("projects_all.json", encoding="utf-8") as f:
    projects = json.load(f)

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

def to_rupees(val):
    if val is None: return None
    return int(val * 1_00_00_000) if val < 10 else int(val * 1_00_000)

# ── 1. Full sorted distribution of price_max ─────────────────────────────────
print("=" * 65)
print("FULL DISTRIBUTION — raw price_max values (sorted)")
print("=" * 65)
pmax_vals = sorted(
    [(p.get("price_max"), p["project_id"]) for p in projects if p.get("price_max") is not None]
)

# Histogram buckets
buckets = {"< 1": 0, "1–2": 0, "2–3": 0, "3–4": 0, "4–5": 0,
           "5–10": 0, "10–20": 0, "20–50": 0, "50–100": 0, ">= 100": 0}
for val, _ in pmax_vals:
    if   val < 1:    buckets["< 1"]   += 1
    elif val < 2:    buckets["1–2"]   += 1
    elif val < 3:    buckets["2–3"]   += 1
    elif val < 4:    buckets["3–4"]   += 1
    elif val < 5:    buckets["4–5"]   += 1
    elif val < 10:   buckets["5–10"]  += 1
    elif val < 20:   buckets["10–20"] += 1
    elif val < 50:   buckets["20–50"] += 1
    elif val < 100:  buckets["50–100"]+= 1
    else:            buckets[">= 100"]+= 1

print(f"\n  {'bucket':<12} {'count':>6}")
print(f"  {'-'*12} {'-'*6}")
for b, c in buckets.items():
    bar = "#" * min(c, 60)
    print(f"  {b:<12} {c:>6}  {bar}")

print(f"\n  Min raw price_max : {pmax_vals[0][0]}  (project {pmax_vals[0][1]})")
print(f"  Max raw price_max : {pmax_vals[-1][0]}  (project {pmax_vals[-1][1]})")


# ── 2. Boundary zone: all values between 5 and 15 ────────────────────────────
print(f"\n{'=' * 65}")
print("BOUNDARY ZONE — all raw price_max values between 5 and 15")
print("(is there a clean gap at 10, or ambiguous middle ground?)")
print("=" * 65)

boundary = [(val, pid) for val, pid in pmax_vals if 5 <= val <= 15]
print(f"\n  Found {len(boundary)} projects in the 5–15 range:\n")
print(f"  {'raw_val':>8}  {'project_id':<10}  {'price_min':>10}  "
      f"{'min_area':>8}  {'max_area':>8}  {'developer':<18} locality")
print(f"  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*8}  {'-'*18} {'-'*12}")
for val, pid in boundary:
    p = next(x for x in projects if x["project_id"] == pid)
    pmin = p.get("price_min", "")
    print(f"  {val:>8.2f}  {pid:<10}  {str(pmin):>10}  "
          f"{str(p.get('min_area_sqft','')or''):>8}  "
          f"{str(p.get('max_area_sqft','')or''):>8}  "
          f"{str(p.get('developer_name','')):<18} {p.get('locality','')}")


# ── 3. Cross-check price_max vs price_min after normalisation ─────────────────
print(f"\n{'=' * 65}")
print("CROSS-CHECK — price_max vs price_min (normalised to rupees)")
print("price_max must always >= price_min")
print("=" * 65)

violations = []
checks = []
for p in projects:
    pmax = p.get("price_max"); pmin = p.get("price_min")
    if pmax is None or pmin is None: continue
    max_inr = to_rupees(pmax)
    min_inr = to_rupees(pmin)
    ratio = max_inr / min_inr if min_inr else None
    checks.append((p["project_id"], pmin, pmax, min_inr, max_inr, ratio))
    if max_inr < min_inr:
        violations.append((p["project_id"], pmin, pmax, min_inr, max_inr))

print(f"\n  Total projects checked : {len(checks)}")
print(f"  Violations (max < min) : {len(violations)}")

if violations:
    print(f"\n  VIOLATIONS:")
    for pid, pmin, pmax, min_inr, max_inr in violations:
        print(f"    {pid}  raw_min={pmin}  raw_max={pmax}  "
              f"→ ₹{min_inr:,} vs ₹{max_inr:,}")
else:
    print("  ✓ No violations — all price_max >= price_min after normalisation")

# Sample 10 to eyeball ratios
print(f"\n  Sample 10 projects (price_min → price_max normalised):")
print(f"  {'project_id':<10} {'raw_min':>8} {'raw_max':>8} "
      f"{'min_inr':>14} {'max_inr':>14} {'ratio':>6}  area_range")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*14} {'-'*14} {'-'*6}  {'-'*15}")
for pid, pmin, pmax, min_inr, max_inr, ratio in checks[:10]:
    p = next(x for x in projects if x["project_id"] == pid)
    area = f"{p.get('min_area_sqft')}-{p.get('max_area_sqft')} sqft"
    print(f"  {pid:<10} {pmin:>8.2f} {pmax:>8.2f} "
          f"{min_inr:>14,} {max_inr:>14,} {ratio:>6.2f}  {area}")


# ── 4. Compare corrected project prices to listing prices in same locality ────
print(f"\n{'=' * 65}")
print("REALITY CHECK — corrected price_max vs listing prices in same locality")
print("(for the top 10 costliest projects)")
print("=" * 65)

# Build median listing price per locality from listings
loc_prices = defaultdict(list)
for r in listings:
    p = r.get("price"); loc = r.get("locality")
    if p and p > 0 and loc:
        loc_prices[loc].append(p)
loc_median = {loc: statistics.median(prices) for loc, prices in loc_prices.items()}

top10 = sorted(
    [(to_rupees(p.get("price_max")), p["project_id"]) for p in projects if p.get("price_max") is not None],
    reverse=True
)[:10]
by_pid = {p["project_id"]: p for p in projects}

print(f"\n  {'project_id':<10} {'corrected_max':>15} {'max_area_sqft':>14} "
      f"{'implied_ppsf':>13} {'loc_median_price':>17} locality")
print(f"  {'-'*10} {'-'*15} {'-'*14} {'-'*13} {'-'*17} {'-'*14}")
for max_inr, pid in top10:
    p = by_pid[pid]
    max_area = p.get("max_area_sqft")
    loc = p.get("locality", "")
    implied_ppsf = max_inr / max_area if max_area else None
    loc_med = loc_median.get(loc)
    ppsf_str = f"{implied_ppsf:>10,.0f}" if implied_ppsf else "N/A"
    loc_str  = f"{loc_med:>14,.0f}" if loc_med else "N/A"
    print(f"  {pid:<10} {max_inr:>15,} {str(max_area or ''):>14} "
          f"{ppsf_str:>13} {loc_str:>17} {loc}")
