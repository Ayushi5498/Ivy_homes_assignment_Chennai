# calc_listings_last_7_days.py
#
# HOW TO RUN:
#   python calc_listings_last_7_days.py
#
# Counts listings posted in [2026-09-03T00:00:00+05:30, 2026-09-10T00:00:00+05:30)

import json
from datetime import datetime, timezone, timedelta
from collections import Counter

IST = timezone(timedelta(hours=5, minutes=30))

# Window in IST
WINDOW_START = datetime(2026, 9, 3,  0, 0, 0, tzinfo=IST)   # inclusive
WINDOW_END   = datetime(2026, 9, 10, 0, 0, 0, tzinfo=IST)   # exclusive

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

print(f"Total listings loaded : {len(listings)}")
print(f"Window (IST)          : [{WINDOW_START.isoformat()}  →  {WINDOW_END.isoformat()})\n")

# ── Parse and filter ──────────────────────────────────────────────────────────
in_window  = []
parse_fail = []

for r in listings:
    posted_at_str = r.get("posted_at")
    if not posted_at_str:
        parse_fail.append(r["listing_id"])
        continue
    try:
        # Parse UTC timestamp (Z suffix)
        dt_utc = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00"))
        dt_ist = dt_utc.astimezone(IST)
    except ValueError:
        parse_fail.append(r["listing_id"])
        continue

    if WINDOW_START <= dt_ist < WINDOW_END:
        in_window.append((dt_ist, r["listing_id"]))

in_window.sort()   # sort by timestamp for edge-case inspection

print(f"Parse failures       : {len(parse_fail)}")
print(f"Records in window    : {len(in_window)}  <- ANSWER")

# ── Date distribution within the window ──────────────────────────────────────
date_counts = Counter(dt.date() for dt, _ in in_window)
print(f"\nDistinct IST dates in window : {len(date_counts)}")
print(f"Records per date:")
for d in sorted(date_counts):
    print(f"  {d}  :  {date_counts[d]:>4} records")

# ── Edge-case boundary inspection ────────────────────────────────────────────
print(f"\n{'=' * 65}")
print("BOUNDARY INSPECTION")
print("=" * 65)

# Earliest 3 included
print(f"\n  Earliest 3 INCLUDED (just after window start {WINDOW_START.date()}):")
for dt_ist, lid in in_window[:3]:
    print(f"    {lid}  posted_at_IST={dt_ist.isoformat()}")

# Latest 3 included
print(f"\n  Latest 3 INCLUDED (just before window end {WINDOW_END.date()}):")
for dt_ist, lid in in_window[-3:]:
    print(f"    {lid}  posted_at_IST={dt_ist.isoformat()}")

# Find records just outside the window (before start and at/after end)
just_before = []
just_after  = []
for r in listings:
    posted_at_str = r.get("posted_at")
    if not posted_at_str: continue
    try:
        dt_ist = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00")).astimezone(IST)
    except ValueError:
        continue
    if dt_ist < WINDOW_START:
        just_before.append((dt_ist, r["listing_id"]))
    elif dt_ist >= WINDOW_END:
        just_after.append((dt_ist, r["listing_id"]))

just_before.sort(reverse=True)   # closest to window start
just_after.sort()                 # closest to window end

print(f"\n  Latest 3 EXCLUDED (just before window start — should be < 2026-09-03T00:00 IST):")
for dt_ist, lid in just_before[:3]:
    print(f"    {lid}  posted_at_IST={dt_ist.isoformat()}")

print(f"\n  Earliest 3 EXCLUDED (just after window end — should be >= 2026-09-10T00:00 IST):")
for dt_ist, lid in just_after[:3]:
    print(f"    {lid}  posted_at_IST={dt_ist.isoformat()}")
