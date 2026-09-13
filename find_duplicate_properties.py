# find_duplicate_properties.py
#
# HOW TO RUN:
#   python find_duplicate_properties.py
#
# Groups listing records into "same physical property" clusters using:
#   - Coordinates within 30 m of each other (haversine)
#   - Same floor
#   - Same bedroom count
#   - Same locality
#   - carpet_area and super_built_up_area within 5% of each other
#
# Uses Union-Find (disjoint set) for efficient clustering.

import json
import math
from collections import defaultdict


# ── Haversine ─────────────────────────────────────────────────────────────────

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


# ── Union-Find (disjoint set) ─────────────────────────────────────────────────

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


# ── Area similarity check ─────────────────────────────────────────────────────

def areas_within_pct(a1, a2, pct=5.0) -> bool:
    """Return True if a1 and a2 are within pct% of each other, or either is missing."""
    if a1 is None or a2 is None or a1 == 0 or a2 == 0:
        return True   # can't compare — don't reject on this basis
    diff = abs(a1 - a2) / max(a1, a2)
    return diff <= (pct / 100.0)


# ── Load data ─────────────────────────────────────────────────────────────────

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

n = len(listings)
print(f"Loaded {n} listings\n")


# ── Build spatial buckets to avoid O(n²) full comparison ─────────────────────
# Round lat/lon to ~0.001° (~110 m) grid cells; compare within same and adjacent cells.

COORD_DIST_M  = 30.0   # max distance to be "same property"
GRID_DEG      = 0.001  # ~111 m per degree → 0.001° ≈ 111 m  (coarse bucket)

def grid_key(lat, lon):
    return (round(lat / GRID_DEG), round(lon / GRID_DEG))

# Map grid cell → list of listing indices
grid: dict[tuple, list[int]] = defaultdict(list)

for i, rec in enumerate(listings):
    lat = rec.get("latitude")
    lon = rec.get("longitude")
    if lat is not None and lon is not None:
        grid[grid_key(lat, lon)].append(i)


# ── Union-Find merge pass ─────────────────────────────────────────────────────

uf = UnionFind(n)
merges = 0

# Neighbour offsets: same cell + 8 surrounding cells
offsets = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

for i, rec_i in enumerate(listings):
    lat_i = rec_i.get("latitude")
    lon_i = rec_i.get("longitude")
    if lat_i is None or lon_i is None:
        continue

    gk = grid_key(lat_i, lon_i)

    # Collect candidate indices from this cell and its 8 neighbours
    candidates = []
    for dr, dc in offsets:
        candidates.extend(grid.get((gk[0]+dr, gk[1]+dc), []))

    for j in candidates:
        if j <= i:
            continue   # only check each pair once

        rec_j = listings[j]
        lat_j = rec_j.get("latitude")
        lon_j = rec_j.get("longitude")
        if lat_j is None or lon_j is None:
            continue

        # ── Gate 1: same locality (fast string check) ──────────────────────
        loc_i = (rec_i.get("locality") or "").strip().lower()
        loc_j = (rec_j.get("locality") or "").strip().lower()
        if loc_i != loc_j:
            continue

        # ── Gate 2: same floor ─────────────────────────────────────────────
        if rec_i.get("floor") != rec_j.get("floor"):
            continue

        # ── Gate 3: same bedroom count ─────────────────────────────────────
        if rec_i.get("bedroom") != rec_j.get("bedroom"):
            continue

        # ── Gate 4: coordinate distance ≤ 30 m ────────────────────────────
        dist = haversine_m(lat_i, lon_i, lat_j, lon_j)
        if dist > COORD_DIST_M:
            continue

        # ── Gate 5: carpet_area and super_built_up_area within 5% ─────────
        if not areas_within_pct(rec_i.get("carpet_area"), rec_j.get("carpet_area")):
            continue
        if not areas_within_pct(rec_i.get("super_built_up_area"), rec_j.get("super_built_up_area")):
            continue

        # All gates passed → same physical property
        uf.union(i, j)
        merges += 1

print(f"Pairs merged as same property: {merges}\n")


# ── Build clusters from Union-Find roots ──────────────────────────────────────

clusters: dict[int, list[int]] = defaultdict(list)
for i in range(n):
    clusters[uf.find(i)].append(i)

all_clusters      = list(clusters.values())
multi_clusters    = [c for c in all_clusters if len(c) > 1]
singleton_clusters = [c for c in all_clusters if len(c) == 1]

listings_in_multi    = sum(len(c) for c in multi_clusters)
listings_as_singletons = len(singleton_clusters)

distinct_properties = len(all_clusters)


# ── Summary ───────────────────────────────────────────────────────────────────

print("=" * 60)
print("DISTINCT PROPERTY COUNT")
print("=" * 60)
print(f"  Total listings                    : {n}")
print(f"  Distinct property groups          : {distinct_properties}  ← ANSWER TO Q2")
print(f"  Groups with > 1 listing (dupes)   : {len(multi_clusters)}")
print(f"  Singleton groups (unique listings): {len(singleton_clusters)}")
print(f"  Listings in multi-listing groups  : {listings_in_multi}")
print(f"  Listings with no match            : {listings_as_singletons}")
print()


# ── Sample 10 multi-listing groups ────────────────────────────────────────────

print("=" * 60)
print("SAMPLE — 10 groups with more than 1 listing")
print("(eyeball these to verify grouping quality)")
print("=" * 60)

# Sort by group size descending for interesting examples
multi_clusters.sort(key=len, reverse=True)
sample_groups = multi_clusters[:10]

for rank, cluster in enumerate(sample_groups, 1):
    recs = [listings[i] for i in cluster]
    print(f"\n  Group {rank}  ({len(recs)} listings)")
    print(f"  {'listing_id':<18} {'apartment_name':<28} {'website':<14} "
          f"{'floor':<6} {'bed':<4} {'lat':<10} {'lon':<10} {'locality'}")
    print(f"  {'-'*18} {'-'*28} {'-'*14} {'-'*6} {'-'*4} {'-'*10} {'-'*10} {'-'*15}")
    for rec in recs:
        lid   = str(rec.get("listing_id", ""))
        aname = str(rec.get("apartment_name", ""))[:27]
        web   = str(rec.get("website", ""))[:13]
        floor = str(rec.get("floor", ""))
        bed   = str(rec.get("bedroom", ""))
        lat   = str(rec.get("latitude", ""))
        lon   = str(rec.get("longitude", ""))
        loc   = str(rec.get("locality", ""))
        print(f"  {lid:<18} {aname:<28} {web:<14} {floor:<6} {bed:<4} {lat:<10} {lon:<10} {loc}")

print()
