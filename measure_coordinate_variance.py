# measure_coordinate_variance.py
#
# HOW TO RUN:
#   python measure_coordinate_variance.py
#
# Measures how much lat/lon varies between listings that share the same project_id,
# using the haversine formula for accurate distances in metres.

import json
import math
from collections import defaultdict
from itertools import combinations


# ── Haversine formula ─────────────────────────────────────────────────────────

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    """Return the great-circle distance in metres between two lat/lon points."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ── Load data ─────────────────────────────────────────────────────────────────

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

print(f"Loaded {len(listings)} listings\n")


# ── Group by project_id (non-null/empty only) ─────────────────────────────────

groups: dict[str, list] = defaultdict(list)
skipped = 0

for rec in listings:
    pid = rec.get("project_id")
    lat = rec.get("latitude")
    lon = rec.get("longitude")
    if not pid:          # null or empty string
        skipped += 1
        continue
    if lat is None or lon is None:
        skipped += 1
        continue
    groups[pid].append(rec)

multi_groups = {pid: recs for pid, recs in groups.items() if len(recs) > 1}

print(f"Records with a valid project_id and coordinates : {len(listings) - skipped}")
print(f"Records skipped (no project_id or no coords)    : {skipped}")
print(f"Unique project_id groups                        : {len(groups)}")
print(f"Groups with > 1 listing                         : {len(multi_groups)}")
print()


# ── Compute all pairwise distances per group ──────────────────────────────────

all_distances = []          # every pairwise distance across all multi-groups
group_stats   = []          # (project_id, n_listings, distances, floor_match, bed_match)

for pid, recs in multi_groups.items():
    distances = []
    floor_matches = []
    bed_matches   = []
    floor_total_matches = []

    for r1, r2 in combinations(recs, 2):
        d = haversine_m(r1["latitude"], r1["longitude"],
                        r2["latitude"], r2["longitude"])
        distances.append(d)
        all_distances.append(d)

        floor_matches.append(r1.get("floor") == r2.get("floor"))
        bed_matches.append(r1.get("bedroom") == r2.get("bedroom"))
        floor_total_matches.append(r1.get("total_floors") == r2.get("total_floors"))

    group_stats.append({
        "project_id"    : pid,
        "n"             : len(recs),
        "distances"     : distances,
        "min_m"         : min(distances),
        "max_m"         : max(distances),
        "avg_m"         : sum(distances) / len(distances),
        "floor_match"   : all(floor_matches),
        "bed_match"     : all(bed_matches),
        "tf_match"      : all(floor_total_matches),
    })


# ── Overall summary ───────────────────────────────────────────────────────────

print("=" * 60)
print("OVERALL DISTANCE SUMMARY (all listings within same project_id)")
print("=" * 60)
if all_distances:
    print(f"  Total pairwise distances measured : {len(all_distances)}")
    print(f"  Minimum distance                  : {min(all_distances):.2f} m")
    print(f"  Maximum distance                  : {max(all_distances):.2f} m")
    print(f"  Average distance                  : {sum(all_distances)/len(all_distances):.2f} m")
    # Buckets
    under_1m   = sum(1 for d in all_distances if d < 1)
    under_10m  = sum(1 for d in all_distances if d < 10)
    under_100m = sum(1 for d in all_distances if d < 100)
    over_1km   = sum(1 for d in all_distances if d >= 1000)
    print(f"\n  Distance distribution:")
    print(f"    < 1 m      : {under_1m:>6}  ({100*under_1m/len(all_distances):.1f}%)")
    print(f"    < 10 m     : {under_10m:>6}  ({100*under_10m/len(all_distances):.1f}%)")
    print(f"    < 100 m    : {under_100m:>6}  ({100*under_100m/len(all_distances):.1f}%)")
    print(f"    >= 1 000 m : {over_1km:>6}  ({100*over_1km/len(all_distances):.1f}%)")
print()


# ── Example groups ────────────────────────────────────────────────────────────

# Sort by max distance descending so we see the most spread-out groups first
group_stats.sort(key=lambda x: x["max_m"], reverse=True)

print("=" * 60)
print("EXAMPLE GROUPS — top 5 by maximum intra-group distance")
print("=" * 60)
for gs in group_stats[:5]:
    print(f"\n  project_id : {gs['project_id']}")
    print(f"  listings   : {gs['n']}")
    print(f"  distances  : min={gs['min_m']:.2f} m  max={gs['max_m']:.2f} m  avg={gs['avg_m']:.2f} m")
    print(f"  floor always matches     : {gs['floor_match']}")
    print(f"  bedroom always matches   : {gs['bed_match']}")
    print(f"  total_floors matches     : {gs['tf_match']}")

print()
print("=" * 60)
print("EXAMPLE GROUPS — 5 with smallest maximum intra-group distance")
print("=" * 60)
for gs in group_stats[-5:]:
    print(f"\n  project_id : {gs['project_id']}")
    print(f"  listings   : {gs['n']}")
    print(f"  distances  : min={gs['min_m']:.2f} m  max={gs['max_m']:.2f} m  avg={gs['avg_m']:.2f} m")
    print(f"  floor always matches     : {gs['floor_match']}")
    print(f"  bedroom always matches   : {gs['bed_match']}")
    print(f"  total_floors matches     : {gs['tf_match']}")

print()


# ── Same-unit variance (same project_id + same floor + same bedroom) ──────────

print("=" * 60)
print("SAME-UNIT VARIANCE")
print("(listings sharing project_id + floor + bedroom count)")
print("=" * 60)

same_unit_distances = []
same_unit_examples  = []

for pid, recs in multi_groups.items():
    # Sub-group by (floor, bedroom)
    sub: dict[tuple, list] = defaultdict(list)
    for r in recs:
        key = (r.get("floor"), r.get("bedroom"))
        sub[key].append(r)

    for key, srecs in sub.items():
        if len(srecs) < 2:
            continue
        for r1, r2 in combinations(srecs, 2):
            d = haversine_m(r1["latitude"], r1["longitude"],
                            r2["latitude"], r2["longitude"])
            same_unit_distances.append(d)
            if len(same_unit_examples) < 5:
                same_unit_examples.append({
                    "project_id" : pid,
                    "floor"      : key[0],
                    "bedroom"    : key[1],
                    "listing_ids": [r1.get("listing_id"), r2.get("listing_id")],
                    "distance_m" : d,
                })

if same_unit_distances:
    print(f"  Same-unit pairs found  : {len(same_unit_distances)}")
    print(f"  Minimum distance       : {min(same_unit_distances):.4f} m")
    print(f"  Maximum distance       : {max(same_unit_distances):.2f} m")
    print(f"  Average distance       : {sum(same_unit_distances)/len(same_unit_distances):.4f} m")
    exact_zero = sum(1 for d in same_unit_distances if d == 0.0)
    near_zero  = sum(1 for d in same_unit_distances if d < 0.01)
    print(f"  Exact 0.0 m            : {exact_zero}")
    print(f"  < 0.01 m (effectively same point) : {near_zero}")

    print(f"\n  Sample same-unit pairs:")
    for ex in same_unit_examples:
        print(f"    project={ex['project_id']}  floor={ex['floor']}  bed={ex['bedroom']}  "
              f"ids={ex['listing_ids']}  dist={ex['distance_m']:.4f} m")
else:
    print("  No same-unit pairs found (no two listings share project_id + floor + bedroom).")

print()
