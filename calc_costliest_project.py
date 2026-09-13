# calc_costliest_project.py  (revised)
#
# HOW TO RUN:
#   python calc_costliest_project.py
#
# price_min/price_max in projects_all.json use MIXED UNITS:
#   values < 10  → stored in crores  (e.g. 1.95 = ₹1.95 Cr = ₹1,95,00,000)
#   values >= 10 → stored in lakhs   (e.g. 99.8 = ₹99.8 L = ₹99,80,000)
# This script normalises everything to full rupees before comparing.

import json

with open("projects_all.json", encoding="utf-8") as f:
    projects = json.load(f)

print(f"Total project records loaded: {len(projects)}\n")


def to_rupees(val):
    """Convert a price_max/price_min value to full rupees.
    < 10  → crores  → multiply by 1,00,00,000
    >= 10 → lakhs   → multiply by 1,00,000
    """
    if val is None:
        return None
    if val < 10:
        return int(val * 1_00_00_000)   # crores to rupees
    else:
        return int(val * 1_00_000)       # lakhs to rupees


# ── Normalise and rank ────────────────────────────────────────────────────────
valid = []
for p in projects:
    pm = p.get("price_max")
    if pm is None:
        continue
    rupees = to_rupees(pm)
    valid.append({**p, "_price_max_inr": rupees})

top5 = sorted(valid, key=lambda p: p["_price_max_inr"], reverse=True)[:5]

print("=" * 72)
print("TOP 5 PROJECTS BY price_max (normalised to full rupees)")
print("=" * 72)
print(f"  {'rank':>4}  {'project_id':<10} {'raw_price_max':>14} {'price_max_inr':>16} "
      f"{'developer':<18} locality")
print(f"  {'-'*4}  {'-'*10} {'-'*14} {'-'*16} {'-'*18} {'-'*15}")
for i, p in enumerate(top5, 1):
    unit = "Cr" if p["price_max"] < 10 else "L"
    print(f"  {i:>4}  {p['project_id']:<10} "
          f"{p['price_max']:>12.2f}{unit}  "
          f"{p['_price_max_inr']:>16,}  "
          f"{str(p.get('developer_name','')):<18} "
          f"{p.get('locality','')}")

# ── Full record of #1 ─────────────────────────────────────────────────────────
best = top5[0]
print(f"\n{'=' * 72}")
print(f"FULL RECORD — #1: {best['project_id']}")
print("=" * 72)
for k, v in best.items():
    if k == "_price_max_inr": continue
    print(f"  {k:<28} {v}")

# ── Final answer ──────────────────────────────────────────────────────────────
print(f"\n{'=' * 72}")
print("FINAL ANSWER")
print("=" * 72)
print(f'  {{"project_id": "{best["project_id"]}", "price_max_inr": {best["_price_max_inr"]}}}')

# ── Sanity: show raw values around the threshold to confirm the unit logic ────
print(f"\n{'=' * 72}")
print("SANITY — raw price_max values near the 10-unit boundary")
print("(confirm: values just below 10 = crores, just above 10 = lakhs)")
print("=" * 72)
near_10 = sorted(valid, key=lambda p: abs(p["price_max"] - 10))[:10]
near_10.sort(key=lambda p: p["price_max"])
for p in near_10:
    unit = "Cr" if p["price_max"] < 10 else "L"
    print(f"  {p['project_id']:<10}  raw={p['price_max']:>6.2f}{unit}  "
          f"→ ₹{p['_price_max_inr']:>14,}  "
          f"area={p.get('min_area_sqft')}-{p.get('max_area_sqft')} sqft  "
          f"{p.get('developer_name','')} / {p.get('locality','')}")
