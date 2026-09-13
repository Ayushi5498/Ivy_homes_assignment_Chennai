# reconcile_project_counts.py
#
# 1. For 3 projects claiming 0 listings but having matched listings:
#    compare project locality/name vs matched listings' locality/name
# 2. For the 124 "accurate" projects: distribution of claimed total_listings
#    to check if accuracy is just small-number coincidence

import json, math
from collections import Counter

with open("projects_all.json", encoding="utf-8") as f:
    projects = json.load(f)

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

by_pid = {p["project_id"]: p for p in projects}

actual_counts = Counter(r.get("project_id") for r in listings if r.get("project_id"))

# Rebuild results
results = []
for p in projects:
    pid     = p["project_id"]
    claimed = p.get("total_listings", 0) or 0
    actual  = actual_counts.get(pid, 0)
    results.append({"project_id": pid, "claimed": claimed, "actual": actual,
                     "diff": actual - claimed})

claims_zero_has_actual = [r for r in results if r["claimed"] == 0 and r["actual"] > 0]
accurate               = [r for r in results if r["diff"] == 0]

# Index listings by project_id
listings_by_pid: dict[str, list] = {}
for r in listings:
    pid = r.get("project_id")
    if pid:
        listings_by_pid.setdefault(pid, []).append(r)

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin(math.radians(lat2-lat1)/2)**2 + \
        math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 2 * R * math.asin(math.sqrt(a))


# ── PART 1: 3 "claims 0 but has matched listings" examples ────────────────────

print("=" * 70)
print("PART 1 — 3 projects claiming 0 listings, but matched listings found")
print("Are the matches geographically/logically related to the project?")
print("=" * 70)

for rec in claims_zero_has_actual[:3]:
    pid  = rec["project_id"]
    proj = by_pid[pid]
    matched = listings_by_pid.get(pid, [])

    proj_lat = proj.get("latitude")
    proj_lon = proj.get("longitude")

    print(f"\n  PROJECT: {pid}")
    print(f"    apartment_name : {proj.get('apartment_name')}")
    print(f"    developer      : {proj.get('developer_name')}")
    print(f"    locality       : {proj.get('locality')}")
    print(f"    lat/lon        : {proj_lat}, {proj_lon}")
    print(f"    total_listings : {proj.get('total_listings')} (claimed)")
    print(f"    actual matched : {len(matched)}")
    print(f"\n  MATCHED LISTINGS ({len(matched)} total — showing all):")
    print(f"  {'listing_id':<18} {'apartment_name':<28} {'locality':<14} "
          f"{'lat':>10} {'lon':>10} {'dist_to_proj':>13}")
    print(f"  {'-'*18} {'-'*28} {'-'*14} {'-'*10} {'-'*10} {'-'*13}")
    for r in matched:
        rlat = r.get("latitude"); rlon = r.get("longitude")
        if proj_lat and rlat:
            dist = haversine_m(proj_lat, proj_lon, rlat, rlon)
            dist_str = f"{dist:>10,.0f} m"
        else:
            dist_str = "N/A"
        print(f"  {r.get('listing_id',''):<18} "
              f"{str(r.get('apartment_name',''))[:27]:<28} "
              f"{str(r.get('locality','')):<14} "
              f"{str(rlat or ''):>10} {str(rlon or ''):>10} {dist_str:>13}")


# ── PART 2: Distribution of claimed total_listings for the 124 "accurate" ────

print(f"\n{'=' * 70}")
print("PART 2 — Distribution of claimed total_listings among 124 'accurate' projects")
print("(accurate = actual count exactly equals claimed)")
print("=" * 70)

claimed_dist = Counter(r["claimed"] for r in accurate)

print(f"\n  {'claimed':>8}  {'# projects':>10}  {'cumulative%':>12}")
print(f"  {'-'*8}  {'-'*10}  {'-'*12}")
total_acc = len(accurate)
cumulative = 0
for val in sorted(claimed_dist.keys()):
    cnt = claimed_dist[val]
    cumulative += cnt
    pct = 100 * cumulative / total_acc
    print(f"  {val:>8}  {cnt:>10}  {pct:>11.1f}%")

zero_or_one = sum(claimed_dist[v] for v in [0, 1] if v in claimed_dist)
two_plus    = sum(cnt for val, cnt in claimed_dist.items() if val >= 2)
print(f"\n  Total 'accurate' projects      : {total_acc}")
print(f"  With claimed = 0 or 1          : {zero_or_one}  "
      f"({100*zero_or_one/total_acc:.0f}%)")
print(f"  With claimed >= 2              : {two_plus}  "
      f"({100*two_plus/total_acc:.0f}%)")

# For claimed >= 2 that are "accurate", show examples — are they really right?
print(f"\n  Examples of 'accurate' projects with claimed >= 5:")
print(f"  {'project_id':<10} {'claimed':>8} {'actual':>8}  {'apartment_name':<28} locality")
print(f"  {'-'*10} {'-'*8} {'-'*8}  {'-'*28} {'-'*14}")
acc_high = [r for r in accurate if r["claimed"] >= 5]
for r in acc_high[:10]:
    proj = by_pid[r["project_id"]]
    print(f"  {r['project_id']:<10} {r['claimed']:>8} {r['actual']:>8}  "
          f"{str(proj.get('apartment_name',''))[:27]:<28} {proj.get('locality','')}")
