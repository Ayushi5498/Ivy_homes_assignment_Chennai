# compare_cutoffs.py — compare cutoff=11 vs cutoff=15 for Check A

import json
import statistics
from collections import defaultdict

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

by_id = {r["listing_id"]: r for r in listings}

CORRUPT_IDS = {
    "100-4000397","100-4000449","100-4000457","100-4000491","100-4000545",
    "100-4000738","100-4001530","100-4001703","100-4002961",
    "DWE-4000236","DWE-4000307","DWE-4000412","DWE-4000824",
    "DWE-4001368","DWE-4001410","DWE-4001424","DWE-4001442",
    "DWE-4002105","DWE-4002247","DWE-4002374","DWE-4002712",
    "DWE-4002806","DWE-4003067","MAG-4000145","MAG-4000283","MAG-4000675",
    "MAG-4001981","MAG-4002776","MAG-4003100","SQU-4000308","SQU-4000459",
    "SQU-4000583","SQU-4001225","SQU-4002391","SQU-4002483","SQU-4002544",
    "ZER-4000021","ZER-4001161","ZER-4001287","ZER-4001669","ZER-4001686",
    "ZER-4001726","ZER-4002091","ZER-4002305","ZER-4002352"
}
clean = [r for r in listings if r["listing_id"] not in CORRUPT_IDS]

# ── Build contact index ───────────────────────────────────────────────────────
contact_to_ids: dict[str, list[str]] = defaultdict(list)
for r in clean:
    c = (r.get("posted_by_contact") or "").strip()
    if c:
        contact_to_ids[c].append(r["listing_id"])

# ── Build Check C refined set (40–70% band, ppsf >= 100) ─────────────────────
MIN_PPSF = 100
group_ppsf: dict[tuple, list] = defaultdict(list)
for r in clean:
    price  = r.get("price")
    carpet = r.get("carpet_area")
    loc    = (r.get("locality") or "").strip().lower()
    bed    = r.get("bedroom")
    if not price or not carpet or carpet <= 0 or not loc or bed is None:
        continue
    ppsf = price / carpet
    if ppsf < MIN_PPSF:
        continue
    group_ppsf[(loc, bed)].append((ppsf, r["listing_id"]))

check_c = set()
for (loc, bed), entries in group_ppsf.items():
    if len(entries) < 5:
        continue
    med = statistics.median(p for p, _ in entries)
    for ppsf, lid in entries:
        if med * 0.40 <= ppsf <= med * 0.70:
            check_c.add(lid)

# ── Compute A∩C for cutoff 11 and 15 ─────────────────────────────────────────
def a_ids_for_cutoff(cutoff):
    return {lid for c, ids in contact_to_ids.items()
            if len(ids) >= cutoff for lid in ids}

a11 = a_ids_for_cutoff(11)
a15 = a_ids_for_cutoff(15)
ac11 = a11 & check_c
ac15 = a15 & check_c

print("=" * 65)
print("CUTOFF COMPARISON: A∩C at cutoff=11 vs cutoff=15")
print("=" * 65)
print(f"\n  cutoff=11 : {len(a11)} A-flagged listings  →  A∩C = {len(ac11)}")
print(f"  cutoff=15 : {len(a15)} A-flagged listings  →  A∩C = {len(ac15)}")
print(f"\n  In cutoff=11 but NOT cutoff=15 (extra 11–14 contact listings): {len(ac11 - ac15)}")
print(f"  In both                                                        : {len(ac11 & ac15)}")

# Side-by-side sorted lists
print(f"\n  {'cutoff=11 A∩C list':<25}  {'cutoff=15 A∩C list'}")
print(f"  {'-'*25}  {'-'*25}")
l11 = sorted(ac11)
l15 = sorted(ac15)
for i in range(max(len(l11), len(l15))):
    a = l11[i] if i < len(l11) else ""
    b = l15[i] if i < len(l15) else ""
    marker = "  " if a == b or not a or not b else "← extra"
    print(f"  {a:<25}  {b:<25} {marker if a and not b else ''}")


# ── Show 3 borderline contacts (10-12 listings each) ─────────────────────────

print("\n" + "=" * 65)
print("BORDERLINE CONTACTS — 3 examples with 10–12 listings each")
print("(are they coherent agent portfolios or scattered farm-like?)")
print("=" * 65)

borderline = [(c, ids) for c, ids in contact_to_ids.items()
              if 10 <= len(ids) <= 12]
# Pick 3 spread across different counts
borderline.sort(key=lambda x: len(x[1]))
# Sample: one at 10, one at 11, one at 12
picks = []
for target in [10, 11, 12]:
    for c, ids in borderline:
        if len(ids) == target and c not in [p[0] for p in picks]:
            picks.append((c, ids))
            break

for contact, ids in picks:
    print(f"\n  Contact: {contact}  ({len(ids)} listings)")
    print(f"  {'listing_id':<18} {'apartment_name':<30} {'locality':<15} "
          f"{'type':<18} {'price':>12}  {'bedroom':>7}  {'floor':>5}")
    print(f"  {'-'*18} {'-'*30} {'-'*15} {'-'*18} {'-'*12}  {'-'*7}  {'-'*5}")
    for lid in ids:
        r = by_id.get(lid, {})
        print(f"  {lid:<18} {str(r.get('apartment_name',''))[:29]:<30} "
              f"{str(r.get('locality',''))[:14]:<15} "
              f"{str(r.get('property_type',''))[:17]:<18} "
              f"{r.get('price',0):>12,}  "
              f"{str(r.get('bedroom','')):>7}  "
              f"{str(r.get('floor','')):>5}")

    # Diversity indicators
    localities  = {by_id[l].get("locality","") for l in ids}
    apt_names   = {by_id[l].get("apartment_name","") for l in ids}
    prop_types  = {by_id[l].get("property_type","") for l in ids}
    prices      = [by_id[l].get("price",0) for l in ids if by_id[l].get("price")]
    print(f"\n  Diversity summary:")
    print(f"    Unique localities   : {len(localities)} → {sorted(localities)}")
    print(f"    Unique apt names    : {len(apt_names)}")
    print(f"    Unique prop types   : {sorted(prop_types)}")
    if prices:
        print(f"    Price range         : ₹{min(prices):,} – ₹{max(prices):,}")
