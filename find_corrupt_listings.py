# find_corrupt_listings.py
#
# HOW TO RUN:
#   python find_corrupt_listings.py
#
# Runs 11 independent sanity checks on listings_all.json and reports
# each check's failures separately, then a combined unique corrupt set.

import json
from datetime import datetime, timezone

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

print(f"Loaded {len(listings)} listings\n")

CUTOFF_DATE = datetime(2026, 9, 13, tzinfo=timezone.utc)   # "today" per assignment

all_corrupt_ids = set()   # accumulates across all checks


def report(check_name, failures, field_fn):
    """
    Print results for one check.
    failures : list of listing dicts that failed
    field_fn : callable(rec) -> str  — returns the offending field values as a string
    """
    ids = [r["listing_id"] for r in failures if r.get("listing_id")]
    all_corrupt_ids.update(ids)

    print(f"{'─'*60}")
    print(f"{check_name}")
    print(f"  Failed : {len(failures)} records")
    if failures:
        print(f"  Examples (up to 5):")
        for rec in failures[:5]:
            print(f"    {rec.get('listing_id','?'):20s}  {field_fn(rec)}")
    print()


# ── CHECK 1: floor > total_floors ─────────────────────────────────────────────
failed = [
    r for r in listings
    if r.get("floor") is not None
    and r.get("total_floors") is not None
    and r["floor"] > r["total_floors"]
]
report(
    "CHECK 1 — floor > total_floors",
    failed,
    lambda r: f"floor={r['floor']}  total_floors={r['total_floors']}"
)

# ── CHECK 2: total_floors <= 0  OR  floor < 0 ─────────────────────────────────
failed = [
    r for r in listings
    if (r.get("total_floors") is not None and r["total_floors"] <= 0)
    or (r.get("floor") is not None and r["floor"] < 0)
]
report(
    "CHECK 2 — total_floors <= 0  OR  floor < 0",
    failed,
    lambda r: f"floor={r.get('floor')}  total_floors={r.get('total_floors')}"
)

# ── CHECK 3: carpet_area > super_built_up_area ────────────────────────────────
failed = [
    r for r in listings
    if r.get("carpet_area") is not None
    and r.get("super_built_up_area") is not None
    and r["carpet_area"] > r["super_built_up_area"]
]
report(
    "CHECK 3 — carpet_area > super_built_up_area",
    failed,
    lambda r: f"carpet_area={r['carpet_area']}  super_built_up_area={r['super_built_up_area']}"
)

# ── CHECK 4: carpet_area <= 0  OR  super_built_up_area <= 0 ──────────────────
failed = [
    r for r in listings
    if (r.get("carpet_area") is not None and r["carpet_area"] <= 0)
    or (r.get("super_built_up_area") is not None and r["super_built_up_area"] <= 0)
]
report(
    "CHECK 4 — carpet_area <= 0  OR  super_built_up_area <= 0",
    failed,
    lambda r: f"carpet_area={r.get('carpet_area')}  super_built_up_area={r.get('super_built_up_area')}"
)

# ── CHECK 5: bedroom <= 0 ─────────────────────────────────────────────────────
failed = [
    r for r in listings
    if r.get("bedroom") is not None and r["bedroom"] <= 0
]
report(
    "CHECK 5 — bedroom <= 0",
    failed,
    lambda r: f"bedroom={r['bedroom']}"
)

# ── CHECK 6: bathroom < 0  OR  balcony < 0  OR  covered_parking < 0 ──────────
failed = [
    r for r in listings
    if (r.get("bathroom") is not None and r["bathroom"] < 0)
    or (r.get("balcony") is not None and r["balcony"] < 0)
    or (r.get("covered_parking") is not None and r["covered_parking"] < 0)
]
report(
    "CHECK 6 — bathroom < 0  OR  balcony < 0  OR  covered_parking < 0",
    failed,
    lambda r: f"bathroom={r.get('bathroom')}  balcony={r.get('balcony')}  covered_parking={r.get('covered_parking')}"
)

# ── CHECK 7: price <= 0 ───────────────────────────────────────────────────────
failed = [
    r for r in listings
    if r.get("price") is not None and r["price"] <= 0
]
report(
    "CHECK 7 — price <= 0",
    failed,
    lambda r: f"price={r['price']}"
)

# ── CHECK 8: lat/lon outside Chennai bounds (±1 degree) ──────────────────────
LAT_MIN, LAT_MAX = 12.8 - 1, 13.2 + 1   # 11.8 – 14.2
LON_MIN, LON_MAX = 80.0 - 1, 80.3 + 1   # 79.0 – 81.3

failed = [
    r for r in listings
    if r.get("latitude") is not None and r.get("longitude") is not None
    and not (LAT_MIN <= r["latitude"] <= LAT_MAX
             and LON_MIN <= r["longitude"] <= LON_MAX)
]
report(
    "CHECK 8 — lat/lon outside Chennai bounds (±1°): "
    f"lat [{LAT_MIN},{LAT_MAX}], lon [{LON_MIN},{LON_MAX}]",
    failed,
    lambda r: f"lat={r['latitude']}  lon={r['longitude']}"
)

# ── CHECK 9: posted_at is a future date (after 2026-09-13) ───────────────────
def is_future(posted_at_str):
    if not posted_at_str:
        return False
    try:
        dt = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00"))
        return dt > CUTOFF_DATE
    except ValueError:
        return False

failed = [r for r in listings if is_future(r.get("posted_at"))]
report(
    "CHECK 9 — posted_at is a future date (after 2026-09-13)",
    failed,
    lambda r: f"posted_at={r.get('posted_at')}"
)

# ── CHECK 10: property_type not in allowed set ────────────────────────────────
VALID_PROPERTY_TYPES = {"apartment", "villa", "independent house", "plot", "builder floor"}
failed = [
    r for r in listings
    if r.get("property_type") not in VALID_PROPERTY_TYPES
]
report(
    "CHECK 10 — property_type not in allowed set",
    failed,
    lambda r: f"property_type={r.get('property_type')!r}"
)

# ── CHECK 11: furnishing not in allowed set ───────────────────────────────────
VALID_FURNISHING = {"unfurnished", "semi-furnished", "fully-furnished"}
failed = [
    r for r in listings
    if r.get("furnishing") not in VALID_FURNISHING
]
report(
    "CHECK 11 — furnishing not in allowed set",
    failed,
    lambda r: f"furnishing={r.get('furnishing')!r}"
)

# ── COMBINED SUMMARY ──────────────────────────────────────────────────────────
print("=" * 60)
print("COMBINED SUMMARY")
print("=" * 60)
print(f"  Total unique listing_ids failing at least one check: {len(all_corrupt_ids)}")
print()
print("  Sorted corrupt listing_ids:")
for lid in sorted(all_corrupt_ids):
    print(f"    {lid}")
