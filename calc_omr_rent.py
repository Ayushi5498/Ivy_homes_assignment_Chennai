# calc_omr_rent.py
#
# HOW TO RUN:
#   python calc_omr_rent.py
#
# Calculates total monthly rent for rentals in the 'omr' locality.

import json
from collections import Counter

with open("rentals_all.json", encoding="utf-8") as f:
    rentals = json.load(f)

print(f"Total rental records loaded: {len(rentals)}\n")

# ── Step 1: All unique locality values ───────────────────────────────────────
loc_counts = Counter(r.get("locality") for r in rentals)

print("=" * 55)
print("ALL UNIQUE LOCALITY VALUES (sorted, with record counts)")
print("=" * 55)
for loc, count in sorted(loc_counts.items(), key=lambda x: (x[0] or "")):
    marker = " ← TARGET" if loc == "omr" else ""
    print(f"  {repr(loc):<25} {count:>5} records{marker}")

# ── Step 2: Filter to locality == "omr" (exact, case-sensitive) ──────────────
omr = [r for r in rentals if r.get("locality") == "omr"]

print(f"\nRecords matching locality == 'omr' (exact): {len(omr)}")

# ── Step 3: Sum price (monthly rent) ─────────────────────────────────────────
prices      = [r.get("price") for r in omr]
bad_records = [r for r in omr if not r.get("price") or r["price"] <= 0]
valid       = [r for r in omr if r.get("price") and r["price"] > 0]
valid_prices = [r["price"] for r in valid]

total_rent  = sum(valid_prices)
avg_price   = total_rent / len(valid_prices) if valid_prices else 0
median_approx = sorted(valid_prices)[len(valid_prices)//2] if valid_prices else 0

print(f"\n{'=' * 55}")
print("PRICE SUMMARY (monthly rent = 'price' field)")
print("=" * 55)
print(f"  Records with price > 0 : {len(valid)}")
print(f"  Records with price <= 0: {len(bad_records)}")
print(f"  Min  price             : {min(valid_prices):,}")
print(f"  Max  price             : {max(valid_prices):,}")
print(f"  Avg  price             : {avg_price:,.2f}")
print(f"  Median price (approx)  : {median_approx:,}")
print(f"\n  TOTAL MONTHLY RENT     : {total_rent:,}  ← ANSWER")

# ── Step 4: Flag extreme values ───────────────────────────────────────────────
threshold_high = avg_price * 5
threshold_low  = avg_price * 0.1

extreme = [r for r in valid if r["price"] > threshold_high or r["price"] < threshold_low]
if extreme:
    print(f"\n  ⚠ Extreme values flagged (>{threshold_high:,.0f} or <{threshold_low:,.0f}):")
    for r in sorted(extreme, key=lambda x: x["price"], reverse=True)[:10]:
        print(f"    {r.get('listing_id'):<18}  price={r['price']:>10,}  "
              f"locality={r.get('locality')}  bedroom={r.get('bedroom')}")
else:
    print(f"\n  No extreme outliers flagged (all within 0.1×–5× of average).")

if bad_records:
    print(f"\n  Records with price <= 0:")
    for r in bad_records:
        print(f"    {r.get('listing_id')}  price={r.get('price')}")
