# calc_wrong_listing_counts.py
#
# HOW TO RUN:
#   python calc_wrong_listing_counts.py
#
# Compares each project's total_listings field against the actual
# number of listings in listings_all.json with a matching project_id.

import json
from collections import Counter

with open("projects_all.json", encoding="utf-8") as f:
    projects = json.load(f)

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

print(f"Projects loaded : {len(projects)}")
print(f"Listings loaded : {len(listings)}\n")

# ── Count actual listings per project_id ─────────────────────────────────────
actual_counts = Counter(
    r.get("project_id") for r in listings if r.get("project_id")
)

# ── Compare to claimed total_listings ────────────────────────────────────────
results = []
for p in projects:
    pid      = p["project_id"]
    claimed  = p.get("total_listings", 0) or 0
    actual   = actual_counts.get(pid, 0)
    diff     = actual - claimed   # positive = more than claimed, negative = fewer
    results.append({
        "project_id"    : pid,
        "locality"      : p.get("locality", ""),
        "developer"     : p.get("developer_name", ""),
        "apartment_name": p.get("apartment_name", ""),
        "claimed"       : claimed,
        "actual"        : actual,
        "diff"          : diff,
        "abs_diff"      : abs(diff),
    })

wrong = [r for r in results if r["diff"] != 0]
correct = [r for r in results if r["diff"] == 0]

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Total projects              : {len(results)}")
print(f"  Projects with correct count : {len(correct)}")
print(f"  Projects with WRONG count   : {len(wrong)}  <- ANSWER")

# ── Mismatch size distribution ────────────────────────────────────────────────
abs_diffs = [r["abs_diff"] for r in wrong]

buckets = {
    "off by 1"  : sum(1 for d in abs_diffs if d == 1),
    "off by 2-3": sum(1 for d in abs_diffs if 2 <= d <= 3),
    "off by 4-9": sum(1 for d in abs_diffs if 4 <= d <= 9),
    "off by 10+": sum(1 for d in abs_diffs if d >= 10),
}

# Special categories
claims_but_zero_actual = [r for r in wrong if r["claimed"] > 0 and r["actual"] == 0]
has_actual_but_claims_zero = [r for r in wrong if r["claimed"] == 0 and r["actual"] > 0]
more_actual_than_claimed = [r for r in wrong if r["diff"] > 0]
fewer_actual_than_claimed = [r for r in wrong if r["diff"] < 0]

print(f"\n  Mismatch size distribution:")
for bucket, count in buckets.items():
    print(f"    {bucket:<14}: {count:>4}")

print(f"\n  Direction breakdown:")
print(f"    Actual > claimed (more in reality)  : {len(more_actual_than_claimed)}")
print(f"    Actual < claimed (fewer in reality) : {len(fewer_actual_than_claimed)}")
print(f"    Claims listings but zero found      : {len(claims_but_zero_actual)}")
print(f"    Has listings but claims zero        : {len(has_actual_but_claims_zero)}")

if abs_diffs:
    print(f"\n  Abs diff — min={min(abs_diffs)}  max={max(abs_diffs)}  "
          f"avg={sum(abs_diffs)/len(abs_diffs):.1f}")

# ── 5 example wrong projects ──────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print("5 EXAMPLE PROJECTS WITH WRONG total_listings")
print("=" * 60)

# Sort by abs_diff descending for interesting examples, show a mix
wrong_sorted = sorted(wrong, key=lambda r: -r["abs_diff"])
# Pick 2 large mismatches, 2 small, 1 claims-but-zero
examples = wrong_sorted[:2]
small = [r for r in wrong if r["abs_diff"] == 1][:2]
examples += small
if claims_but_zero_actual:
    examples.append(claims_but_zero_actual[0])
# deduplicate
seen = set()
final_examples = []
for r in examples:
    if r["project_id"] not in seen:
        final_examples.append(r)
        seen.add(r["project_id"])

print(f"\n  {'project_id':<10} {'locality':<14} {'developer':<16} "
      f"{'claimed':>8} {'actual':>8} {'diff':>6}  apartment_name")
print(f"  {'-'*10} {'-'*14} {'-'*16} {'-'*8} {'-'*8} {'-'*6}  {'-'*25}")
for r in final_examples[:5]:
    sign = "+" if r["diff"] > 0 else ""
    print(f"  {r['project_id']:<10} {str(r['locality']):<14} "
          f"{str(r['developer']):<16} "
          f"{r['claimed']:>8} {r['actual']:>8} {sign+str(r['diff']):>6}  "
          f"{str(r['apartment_name'])[:30]}")

# ── Full distribution of (claimed, actual) pairs for wrong projects ───────────
print(f"\n{'=' * 60}")
print("DISTRIBUTION OF (claimed, actual) FOR ALL WRONG PROJECTS")
print("=" * 60)
ca_counts = Counter((r["claimed"], r["actual"]) for r in wrong)
print(f"\n  {'claimed':>8} {'actual':>8} {'count':>6}")
print(f"  {'-'*8} {'-'*8} {'-'*6}")
for (claimed, actual), count in sorted(ca_counts.items()):
    print(f"  {claimed:>8} {actual:>8} {count:>6}")
