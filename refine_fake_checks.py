# refine_fake_checks.py
#
# HOW TO RUN:
#   python refine_fake_checks.py
#
# Refined Check A: full contact reuse histogram to find natural cutoff
# Refined Check C: moderate price outliers (40-70% of median), excluding entry errors
# Cross-reference: A ∩ C with various cutoffs

import json
import statistics
from collections import defaultdict, Counter

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

by_id = {r["listing_id"]: r for r in listings}

CORRUPT_IDS = {
    "100-4000397","100-4000449","100-4000457","100-4000491","100-4000545",
    "100-4000738","100-4001530","100-4001703","100-4002961",
    "DWE-4000236","DWE-4000307","DWE-4000412","DWE-4000824",
    "DWE-4001368","DWE-4001410","DWE-4001424","DWE-4001442",
    "DWE-4002105","DWE-4002247","DWE-4002374","DWE-4002712",
    "DWE-4002806","DWE-4003067",
    "MAG-4000145","MAG-4000283","MAG-4000675","MAG-4001981",
    "MAG-4002776","MAG-4003100",
    "SQU-4000308","SQU-4000459","SQU-4000583","SQU-4001225",
    "SQU-4002391","SQU-4002483","SQU-4002544",
    "ZER-4000021","ZER-4001161","ZER-4001287","ZER-4001669",
    "ZER-4001686","ZER-4001726","ZER-4002091","ZER-4002305","ZER-4002352"
}

clean = [r for r in listings if r["listing_id"] not in CORRUPT_IDS]


# ─────────────────────────────────────────────────────────────────────────────
# REFINED CHECK A — full contact reuse histogram
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 65)
print("REFINED CHECK A — CONTACT REUSE FULL HISTOGRAM")
print("=" * 65)

contact_to_ids: dict[str, list[str]] = defaultdict(list)
for r in clean:
    c = (r.get("posted_by_contact") or "").strip()
    if c:
        contact_to_ids[c].append(r["listing_id"])

counts = sorted(len(v) for v in contact_to_ids.values())
count_freq = Counter(counts)   # count_value → how many contacts have that count

print(f"\n  Total unique contacts : {len(contact_to_ids)}")
print(f"  Total listings with a contact : {sum(counts)}\n")

print(f"  {'reuse count':>12}  {'# contacts':>12}  {'# listings':>12}  cumulative%")
print(f"  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*12}")

total_contacts = len(contact_to_ids)
cumulative = 0
# Print every individual value up to 10, then buckets
thresholds = list(range(1, 11)) + [15, 20, 21]
prev = 0
for t in thresholds:
    if t <= 20:
        n_contacts  = count_freq.get(t, 0)
        n_listings  = n_contacts * t
    else:
        # 21+
        n_contacts = sum(v for k, v in count_freq.items() if k >= 21)
        n_listings = sum(k*v for k, v in count_freq.items() if k >= 21)
        t = "21+"
    cumulative += n_contacts
    pct = 100 * cumulative / total_contacts
    print(f"  {str(t):>12}  {n_contacts:>12}  {n_listings:>12}  {pct:>11.1f}%")
    if t == "21+":
        break

# Print the sorted full distribution for values > 10
high_counts = sorted([(k, v) for k, v in count_freq.items() if k > 10], reverse=True)
if high_counts:
    print(f"\n  Detail — contacts with > 10 listings (count: how_many_contacts):")
    for cnt, n_contacts in high_counts:
        print(f"    {cnt:>3} listings/contact × {n_contacts} contacts = {cnt*n_contacts} listings")

# Full top-25 ranked contacts
print(f"\n  Top 25 contacts by listing count:")
top25 = sorted(contact_to_ids.items(), key=lambda x: -len(x[1]))[:25]
print(f"  {'rank':>4}  {'contact':<18}  {'#listings':>9}")
print(f"  {'-'*4}  {'-'*18}  {'-'*9}")
for i, (c, ids) in enumerate(top25, 1):
    print(f"  {i:>4}  {c:<18}  {len(ids):>9}")


# ─────────────────────────────────────────────────────────────────────────────
# REFINED CHECK C — moderate price outliers (40-70% of median)
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("REFINED CHECK C — MODERATE PRICE OUTLIERS (40–70% of median)")
print("(excludes obvious entry errors: ppsf < 100 treated as data error)")
print("=" * 65)

MIN_PPSF    = 100    # below this = likely wrong units (lakhs vs rupees), skip
LOWER_BOUND = 0.40   # 40% of median
UPPER_BOUND = 0.70   # 70% of median
MIN_GROUP   = 5      # minimum group size for stable median

group_ppsf: dict[tuple, list] = defaultdict(list)
skipped_entry_error = 0

for r in clean:
    price  = r.get("price")
    carpet = r.get("carpet_area")
    loc    = (r.get("locality") or "").strip().lower()
    bed    = r.get("bedroom")
    if not price or not carpet or carpet <= 0 or not loc or bed is None:
        continue
    ppsf = price / carpet
    if ppsf < MIN_PPSF:
        skipped_entry_error += 1
        continue
    group_ppsf[(loc, bed)].append((ppsf, r["listing_id"]))

print(f"\n  Listings skipped (ppsf < {MIN_PPSF}, likely entry error): {skipped_entry_error}")

check_c_refined = set()
flagged_c = []

for (loc, bed), entries in group_ppsf.items():
    if len(entries) < MIN_GROUP:
        continue
    median_ppsf = statistics.median(p for p, _ in entries)
    lo = median_ppsf * LOWER_BOUND
    hi = median_ppsf * UPPER_BOUND
    for ppsf, lid in entries:
        if lo <= ppsf <= hi:
            check_c_refined.add(lid)
            r = by_id[lid]
            flagged_c.append({
                "listing_id"  : lid,
                "locality"    : loc,
                "bedroom"     : bed,
                "price"       : r.get("price"),
                "carpet_area" : r.get("carpet_area"),
                "ppsf"        : ppsf,
                "median_ppsf" : median_ppsf,
                "ratio"       : ppsf / median_ppsf,
            })

flagged_c.sort(key=lambda x: x["ratio"])

print(f"\n  Groups analysed (>= {MIN_GROUP} listings): "
      f"{sum(1 for e in group_ppsf.values() if len(e)>=MIN_GROUP)}")
print(f"  Listings in 40–70% band: {len(check_c_refined)}")

print(f"\n  Sample — 15 examples from the 40-70% band (most extreme first):")
print(f"  {'listing_id':<18} {'locality':<14} {'bed':>4} {'price':>12} "
      f"{'carpet':>7} {'ppsf':>8} {'median':>8} {'ratio':>6}")
print(f"  {'-'*18} {'-'*14} {'-'*4} {'-'*12} {'-'*7} {'-'*8} {'-'*8} {'-'*6}")
for f in flagged_c[:15]:
    print(f"  {f['listing_id']:<18} {f['locality']:<14} {f['bedroom']:>4} "
          f"{f['price']:>12,} {f['carpet_area']:>7} "
          f"{f['ppsf']:>8.0f} {f['median_ppsf']:>8.0f} {f['ratio']:>6.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# CROSS-REFERENCE at various Check A cutoffs
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("CROSS-REFERENCE A ∩ C  at various Check A cutoffs")
print("=" * 65)

print(f"\n  {'A cutoff':>10}  {'A flagged':>10}  {'A∩C':>8}")
print(f"  {'-'*10}  {'-'*10}  {'-'*8}")
for cutoff in [5, 8, 10, 12, 15, 20]:
    a_ids = {lid for c, ids in contact_to_ids.items()
             if len(ids) >= cutoff for lid in ids}
    overlap = a_ids & check_c_refined
    print(f"  {cutoff:>10}  {len(a_ids):>10}  {len(overlap):>8}")
