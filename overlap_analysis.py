# overlap_analysis.py — checks overlap between the 5 "clear" corruption checks
# and full record inspection of floor=0 and bedroom=0 groups

import json
from datetime import datetime, timezone

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

CUTOFF_DATE = datetime(2026, 9, 13, tzinfo=timezone.utc)

def is_future(s):
    if not s: return False
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")) > CUTOFF_DATE
    except ValueError:
        return False

# ── Rebuild the 5 "clear" check sets ─────────────────────────────────────────

c1 = {r["listing_id"] for r in listings
      if r.get("floor") is not None and r.get("total_floors") is not None
      and r["floor"] > r["total_floors"]}

c3 = {r["listing_id"] for r in listings
      if r.get("carpet_area") is not None and r.get("super_built_up_area") is not None
      and r["carpet_area"] > r["super_built_up_area"]}

c7 = {r["listing_id"] for r in listings
      if r.get("price") is not None and r["price"] <= 0}

# Check 8: lat/lon swapped (values that look like lon are in lat field)
# Chennai lat ~12.8-13.2, lon ~80.0-80.3  ±1 degree
c8 = {r["listing_id"] for r in listings
      if r.get("latitude") is not None and r.get("longitude") is not None
      and not (11.8 <= r["latitude"] <= 14.2 and 79.0 <= r["longitude"] <= 81.3)}

c9 = {r["listing_id"] for r in listings if is_future(r.get("posted_at"))}

checks = {"C1 floor>total_floors": c1,
          "C3 carpet>SBA":         c3,
          "C7 price<=0":           c7,
          "C8 swapped coords":     c8,
          "C9 future date":        c9}

# ── 1. Venn/overlap breakdown ─────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — OVERLAP BETWEEN 5 CLEAR CORRUPTION CHECKS")
print("=" * 60)

print("\nIndividual counts:")
for name, s in checks.items():
    print(f"  {name:<25} : {len(s):>3} ids")

all5 = c1 | c3 | c7 | c8 | c9
print(f"\n  UNION (unique across all 5) : {len(all5)}")

# Pairwise overlaps
names = list(checks.keys())
sets  = list(checks.values())
print("\nPairwise overlaps (only non-zero pairs):")
found_any = False
for i in range(len(names)):
    for j in range(i+1, len(names)):
        overlap = sets[i] & sets[j]
        if overlap:
            print(f"  {names[i]}  ∩  {names[j]}  =  {len(overlap)}  ids: {sorted(overlap)}")
            found_any = True
if not found_any:
    print("  (none — all 5 sets are completely disjoint)")

# Records failing 2+ checks
from collections import Counter
id_check_count = Counter()
for s in sets:
    for lid in s:
        id_check_count[lid] += 1

multi_fail = {lid: cnt for lid, cnt in id_check_count.items() if cnt >= 2}
if multi_fail:
    print(f"\nListing_ids failing 2+ checks:")
    for lid, cnt in sorted(multi_fail.items()):
        which = [name for name, s in checks.items() if lid in s]
        print(f"  {lid}  ({cnt} checks: {', '.join(which)})")
else:
    print("\nNo listing_id fails more than one of the 5 checks.")

print(f"\nFull sorted list of the {len(all5)} unique corrupt ids (checks 1,3,7,8,9):")
for lid in sorted(all5):
    print(f"  {lid}")


# ── 2. Floor=0 examples ───────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 2a — 5 FULL EXAMPLES: floor=0 (and/or total_floors=0)")
print("=" * 60)

floor0 = [r for r in listings
          if (r.get("total_floors") is not None and r["total_floors"] <= 0)
          or (r.get("floor") is not None and r["floor"] < 0)]

FIELDS = ["listing_id","apartment_name","locality","floor","total_floors",
          "bedroom","bathroom","carpet_area","super_built_up_area",
          "price","furnishing","property_type","is_live","posted_at"]

for rec in floor0[:5]:
    print()
    for f in FIELDS:
        print(f"  {f:<25} {rec.get(f)}")

# ── 3. Bedroom=0 examples ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 2b — 5 FULL EXAMPLES: bedroom=0")
print("=" * 60)

bed0 = [r for r in listings
        if r.get("bedroom") is not None and r["bedroom"] <= 0]

for rec in bed0[:5]:
    print()
    for f in FIELDS:
        print(f"  {f:<25} {rec.get(f)}")

# overlap between floor0 and bed0 sets
f0_ids = {r["listing_id"] for r in floor0}
b0_ids = {r["listing_id"] for r in bed0}
print(f"\nOverlap between floor<=0 group and bedroom<=0 group: "
      f"{len(f0_ids & b0_ids)} records "
      f"({100*len(f0_ids & b0_ids)/len(b0_ids):.0f}% of bedroom=0 are also floor=0)")
