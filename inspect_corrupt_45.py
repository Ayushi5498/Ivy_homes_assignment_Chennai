# inspect_corrupt_45.py — deeper look at the 45 confirmed corrupt records

import json
from collections import Counter
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

# ── Rebuild the 5 check sets ──────────────────────────────────────────────────

c1 = {r["listing_id"]: r for r in listings
      if r.get("floor") is not None and r.get("total_floors") is not None
      and r["floor"] > r["total_floors"]}

c3 = {r["listing_id"]: r for r in listings
      if r.get("carpet_area") is not None and r.get("super_built_up_area") is not None
      and r["carpet_area"] > r["super_built_up_area"]}

c7 = {r["listing_id"]: r for r in listings
      if r.get("price") is not None and r["price"] <= 0}

c8 = {r["listing_id"]: r for r in listings
      if r.get("latitude") is not None and r.get("longitude") is not None
      and not (11.8 <= r["latitude"] <= 14.2 and 79.0 <= r["longitude"] <= 81.3)}

c9 = {r["listing_id"]: r for r in listings if is_future(r.get("posted_at"))}

# "plot" records from checks 2/5
plot_ids = {r["listing_id"] for r in listings
            if r.get("property_type") == "plot"
            or (r.get("floor") is not None and r["floor"] <= 0)
            or (r.get("bedroom") is not None and r["bedroom"] <= 0)}

all45_ids = set(c1) | set(c3) | set(c7) | set(c8) | set(c9)
all45_recs = {lid: next(r for r in listings if r["listing_id"] == lid)
              for lid in all45_ids}

checks_map = {
    "C1 floor>total_floors": c1,
    "C3 carpet>SBA":         c3,
    "C7 price<=0":           c7,
    "C8 swapped coords":     c8,
    "C9 future date":        c9,
}


# ── 1. Overlap with plot records ──────────────────────────────────────────────

print("=" * 60)
print("OVERLAP: 45 corrupt IDs  vs  plot/floor=0/bedroom=0 group")
print("=" * 60)
overlap = all45_ids & plot_ids
print(f"  Overlap count : {len(overlap)}")
if overlap:
    print(f"  IDs           : {sorted(overlap)}")
else:
    print("  Confirmed: zero overlap — 45 corrupt records are entirely separate from plot records.")


# ── 2. Per-check property_type and website distribution ──────────────────────

print()
print("=" * 60)
print("PROPERTY_TYPE AND WEBSITE BREAKDOWN — per check")
print("=" * 60)

for check_name, check_dict in checks_map.items():
    recs = list(check_dict.values())
    pt_counts  = Counter(r.get("property_type", "?") for r in recs)
    web_counts = Counter(r.get("website", "?")       for r in recs)
    print(f"\n  {check_name}  ({len(recs)} records)")
    print(f"    property_type : {dict(pt_counts)}")
    print(f"    website       : {dict(web_counts)}")


# ── 3. All 45 combined property_type and website distribution ─────────────────

all45_recs_list = list(all45_recs.values())
print()
print("=" * 60)
print("COMBINED: all 45 corrupt records")
print("=" * 60)
pt_all  = Counter(r.get("property_type", "?") for r in all45_recs_list)
web_all = Counter(r.get("website", "?")       for r in all45_recs_list)
print(f"  property_type : {dict(pt_all)}")
print(f"  website       : {dict(web_all)}")


# ── 4. Check 8 detailed — all 9 swapped-coord records ────────────────────────

print()
print("=" * 60)
print("CHECK 8 — ALL 9 SWAPPED-COORD RECORDS (raw lat/lon)")
print("=" * 60)
print(f"  NOTE: Chennai is roughly lat 12.8–13.2, lon 80.0–80.3")
print(f"  Swapped records will show lat ~80, lon ~13\n")
print(f"  {'listing_id':<20} {'raw_lat':>10}  {'raw_lon':>10}  {'swapped_lat':>12}  {'swapped_lon':>12}  locality")
print(f"  {'-'*20} {'-'*10}  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*15}")

for lid, rec in sorted(c8.items()):
    raw_lat = rec.get("latitude")
    raw_lon = rec.get("longitude")
    # If truly swapped, the "real" values would be lat=raw_lon, lon=raw_lat
    print(f"  {lid:<20} {raw_lat:>10}  {raw_lon:>10}  "
          f"{raw_lon:>12}  {raw_lat:>12}  {rec.get('locality','')}")
