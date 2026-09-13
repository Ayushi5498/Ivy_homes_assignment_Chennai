# find_fake_listings.py
#
# HOW TO RUN:
#   python find_fake_listings.py
#
# Runs 3 independent fake-listing checks and cross-references them
# to surface the strongest multi-signal candidates.

import json
import statistics
from collections import defaultdict, Counter

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

print(f"Loaded {len(listings)} listings\n")

# Index by listing_id for quick lookup
by_id = {r["listing_id"]: r for r in listings}

# ─────────────────────────────────────────────────────────────────────────────
# CHECK A — Reused contact numbers
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 65)
print("CHECK A — REUSED posted_by_contact NUMBERS")
print("=" * 65)

contact_to_ids: dict[str, list[str]] = defaultdict(list)
for r in listings:
    contact = (r.get("posted_by_contact") or "").strip()
    if contact:
        contact_to_ids[contact].append(r["listing_id"])

counts = [len(v) for v in contact_to_ids.values()]

bucket_1   = sum(1 for c in counts if c == 1)
bucket_2_3 = sum(1 for c in counts if 2 <= c <= 3)
bucket_4_9 = sum(1 for c in counts if 4 <= c <= 9)
bucket_10p = sum(1 for c in counts if c >= 10)

print(f"\n  Contact distribution:")
print(f"    Appears on exactly 1 listing   : {bucket_1}")
print(f"    Appears on 2–3 listings         : {bucket_2_3}")
print(f"    Appears on 4–9 listings         : {bucket_4_9}")
print(f"    Appears on 10+ listings         : {bucket_10p}")

# Top 15 most-reused contacts
top15 = sorted(contact_to_ids.items(), key=lambda x: -len(x[1]))[:15]

print(f"\n  Top 15 most-reused contacts:")
print(f"  {'contact':<18} {'#listings':>9}")
print(f"  {'-'*18} {'-'*9}")
for contact, ids in top15:
    print(f"  {contact:<18} {len(ids):>9}")

# Threshold: flag contacts with 10+ listings as suspicious
CONTACT_THRESHOLD = 10
flagged_contacts = {c: ids for c, ids in contact_to_ids.items() if len(ids) >= CONTACT_THRESHOLD}
check_a_ids = set(lid for ids in flagged_contacts.values() for lid in ids)

print(f"\n  Contacts with >= {CONTACT_THRESHOLD} listings: {len(flagged_contacts)}")
print(f"  Total listing_ids flagged by Check A: {len(check_a_ids)}")

print(f"\n  Sample listings for the top 3 contacts (5 each):")
for contact, ids in top15[:3]:
    print(f"\n    Contact: {contact}  ({len(ids)} listings)")
    print(f"    {'listing_id':<18} {'apartment_name':<28} {'locality':<15} {'type':<18} {'price':>12}")
    print(f"    {'-'*18} {'-'*28} {'-'*15} {'-'*18} {'-'*12}")
    for lid in ids[:5]:
        r = by_id.get(lid, {})
        print(f"    {lid:<18} {str(r.get('apartment_name',''))[:27]:<28} "
              f"{str(r.get('locality',''))[:14]:<15} "
              f"{str(r.get('property_type',''))[:17]:<18} "
              f"{r.get('price', 0):>12,}")


# ─────────────────────────────────────────────────────────────────────────────
# CHECK B — Duplicate descriptions
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("CHECK B — VERBATIM DUPLICATE DESCRIPTIONS")
print("=" * 65)

desc_to_ids: dict[str, list[str]] = defaultdict(list)
for r in listings:
    desc = (r.get("description") or "").strip()
    if desc:
        desc_to_ids[desc].append(r["listing_id"])

dup_groups = {desc: ids for desc, ids in desc_to_ids.items() if len(ids) > 1}
check_b_ids = set(lid for ids in dup_groups.values() for lid in ids)

total_in_dups = sum(len(ids) for ids in dup_groups.values())
print(f"\n  Duplicate description groups : {len(dup_groups)}")
print(f"  Listings involved            : {total_in_dups}")
print(f"  Total listing_ids flagged by Check B: {len(check_b_ids)}")

# Show 5 examples, sorted by group size descending
sorted_dups = sorted(dup_groups.items(), key=lambda x: -len(x[1]))
print(f"\n  5 largest duplicate description groups:")
for desc, ids in sorted_dups[:5]:
    preview = desc[:120].replace("\n", " ")
    print(f"\n    {len(ids)} listings share this description:")
    print(f"    IDs  : {ids}")
    print(f"    Text : \"{preview}{'...' if len(desc)>120 else ''}\"")


# ─────────────────────────────────────────────────────────────────────────────
# CHECK C — Price-per-sqft outliers (< 50% of locality+bedroom median)
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("CHECK C — PRICE-PER-SQFT OUTLIERS (< 50% of locality+bedroom median)")
print("=" * 65)

# Build group → list of (price_per_sqft, listing_id)
group_ppsf: dict[tuple, list] = defaultdict(list)
for r in listings:
    price      = r.get("price")
    carpet     = r.get("carpet_area")
    locality   = (r.get("locality") or "").strip().lower()
    bedroom    = r.get("bedroom")
    if not price or not carpet or carpet <= 0 or not locality or bedroom is None:
        continue
    if r["listing_id"] in {lid for ids in [  # skip corrupt records
        ["100-4000397","100-4000449","100-4000457","100-4000491","100-4000545",
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
         "ZER-4001686","ZER-4001726","ZER-4002091","ZER-4002305",
         "ZER-4002352"]
    ] for lid in ids}:
        continue
    ppsf = price / carpet
    group_ppsf[(locality, bedroom)].append((ppsf, r["listing_id"]))

# Only consider groups with >= 5 listings (too few = noisy median)
MIN_GROUP_SIZE = 5
check_c_ids = set()
flagged_c = []   # (listing_id, ppsf, median_ppsf, locality, bedroom, price, carpet)

for (locality, bedroom), entries in group_ppsf.items():
    if len(entries) < MIN_GROUP_SIZE:
        continue
    median_ppsf = statistics.median(p for p, _ in entries)
    threshold   = median_ppsf * 0.50
    for ppsf, lid in entries:
        if ppsf < threshold:
            check_c_ids.add(lid)
            r = by_id[lid]
            flagged_c.append({
                "listing_id"  : lid,
                "locality"    : locality,
                "bedroom"     : bedroom,
                "price"       : r.get("price"),
                "carpet_area" : r.get("carpet_area"),
                "ppsf"        : ppsf,
                "median_ppsf" : median_ppsf,
                "ratio"       : ppsf / median_ppsf,
            })

flagged_c.sort(key=lambda x: x["ratio"])   # most extreme first

print(f"\n  Groups with >= {MIN_GROUP_SIZE} listings analysed : {sum(1 for e in group_ppsf.values() if len(e)>=MIN_GROUP_SIZE)}")
print(f"  Listings flagged (ppsf < 50% of group median): {len(check_c_ids)}")

print(f"\n  10 most extreme outliers:")
print(f"  {'listing_id':<18} {'locality':<14} {'bed':>4} {'price':>12} {'carpet':>7} "
      f"{'ppsf':>8} {'median':>8} {'ratio':>6}")
print(f"  {'-'*18} {'-'*14} {'-'*4} {'-'*12} {'-'*7} {'-'*8} {'-'*8} {'-'*6}")
for f in flagged_c[:10]:
    print(f"  {f['listing_id']:<18} {f['locality']:<14} {f['bedroom']:>4} "
          f"{f['price']:>12,} {f['carpet_area']:>7} "
          f"{f['ppsf']:>8.0f} {f['median_ppsf']:>8.0f} {f['ratio']:>6.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# CROSS-REFERENCE: multi-signal candidates
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("CROSS-REFERENCE — multi-signal fake-listing candidates")
print("=" * 65)

print(f"\n  Check A flagged : {len(check_a_ids)} listings")
print(f"  Check B flagged : {len(check_b_ids)} listings")
print(f"  Check C flagged : {len(check_c_ids)} listings")

ab = check_a_ids & check_b_ids
ac = check_a_ids & check_c_ids
bc = check_b_ids & check_c_ids
abc = check_a_ids & check_b_ids & check_c_ids
multi = (ab | ac | bc)   # flagged by 2+ checks

print(f"\n  Flagged by A ∩ B (contact + dup desc)   : {len(ab)}  {sorted(ab)}")
print(f"  Flagged by A ∩ C (contact + low price)  : {len(ac)}  {sorted(ac)}")
print(f"  Flagged by B ∩ C (dup desc + low price) : {len(bc)}  {sorted(bc)}")
print(f"  Flagged by all 3 (A ∩ B ∩ C)            : {len(abc)} {sorted(abc)}")

print(f"\n  ── STRONGEST CANDIDATES (2+ checks): {len(multi)} listings ──")
for lid in sorted(multi):
    which = []
    if lid in check_a_ids: which.append("A")
    if lid in check_b_ids: which.append("B")
    if lid in check_c_ids: which.append("C")
    r = by_id.get(lid, {})
    print(f"    {lid:<18} checks={'+'.join(which):<5}  "
          f"{str(r.get('apartment_name',''))[:28]:<28}  {r.get('locality','')}")

print(f"\n  ── SINGLE-CHECK FLAGS ──")
only_a = check_a_ids - check_b_ids - check_c_ids
only_b = check_b_ids - check_a_ids - check_c_ids
only_c = check_c_ids - check_a_ids - check_b_ids

print(f"\n  Only Check A ({len(only_a)} listings — reused contact only):")
for lid in sorted(only_a)[:20]:
    print(f"    {lid}")
if len(only_a) > 20:
    print(f"    ... and {len(only_a)-20} more")

print(f"\n  Only Check B ({len(only_b)} listings — duplicate description only):")
for lid in sorted(only_b):
    print(f"    {lid}")

print(f"\n  Only Check C ({len(only_c)} listings — low price-per-sqft only):")
for lid in sorted(only_c):
    print(f"    {lid}")
