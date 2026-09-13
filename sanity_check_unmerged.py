# sanity_check_unmerged.py
#
# Finds pairs of listings that share the same apartment_name (normalised)
# but were NOT placed in the same deduplication group.
# Shows floor/bedroom/coords/locality side by side so you can judge
# whether keeping them separate was correct.

import json
import math
import re
from collections import defaultdict


# ── Haversine ─────────────────────────────────────────────────────────────────

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


# ── Normalise apartment name for fuzzy matching ───────────────────────────────

def normalise(name: str) -> str:
    """Lowercase, strip punctuation/extra spaces so minor formatting diffs vanish."""
    s = (name or "").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)   # remove hyphens, dots, etc.
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ── Re-run Union-Find to get group assignments ────────────────────────────────
# (same logic as find_duplicate_properties.py)

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
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

def areas_within_pct(a1, a2, pct=5.0):
    if a1 is None or a2 is None or a1 == 0 or a2 == 0:
        return True
    return abs(a1 - a2) / max(a1, a2) <= pct / 100.0

COORD_DIST_M = 30.0
GRID_DEG     = 0.001

def grid_key(lat, lon):
    return (round(lat / GRID_DEG), round(lon / GRID_DEG))

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

n = len(listings)
uf = UnionFind(n)

grid: dict[tuple, list[int]] = defaultdict(list)
for i, rec in enumerate(listings):
    lat, lon = rec.get("latitude"), rec.get("longitude")
    if lat is not None and lon is not None:
        grid[grid_key(lat, lon)].append(i)

offsets = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

for i, rec_i in enumerate(listings):
    lat_i, lon_i = rec_i.get("latitude"), rec_i.get("longitude")
    if lat_i is None or lon_i is None:
        continue
    gk = grid_key(lat_i, lon_i)
    candidates = []
    for dr, dc in offsets:
        candidates.extend(grid.get((gk[0]+dr, gk[1]+dc), []))
    for j in candidates:
        if j <= i:
            continue
        rec_j = listings[j]
        lat_j, lon_j = rec_j.get("latitude"), rec_j.get("longitude")
        if lat_j is None or lon_j is None:
            continue
        if (rec_i.get("locality") or "").strip().lower() != (rec_j.get("locality") or "").strip().lower():
            continue
        if rec_i.get("floor") != rec_j.get("floor"):
            continue
        if rec_i.get("bedroom") != rec_j.get("bedroom"):
            continue
        if haversine_m(lat_i, lon_i, lat_j, lon_j) > COORD_DIST_M:
            continue
        if not areas_within_pct(rec_i.get("carpet_area"), rec_j.get("carpet_area")):
            continue
        if not areas_within_pct(rec_i.get("super_built_up_area"), rec_j.get("super_built_up_area")):
            continue
        uf.union(i, j)


# ── Group by normalised apartment_name ───────────────────────────────────────

name_groups: dict[str, list[int]] = defaultdict(list)
for i, rec in enumerate(listings):
    norm = normalise(rec.get("apartment_name", ""))
    if norm:
        name_groups[norm].append(i)


# ── Find pairs with same name but different dedup groups ─────────────────────

print("Searching for same-name pairs that were NOT merged...\n")

unmerged_pairs = []

for norm_name, indices in name_groups.items():
    if len(indices) < 2:
        continue
    # Check all pairs in this name group
    for a in range(len(indices)):
        for b in range(a + 1, len(indices)):
            i, j = indices[a], indices[b]
            if uf.find(i) != uf.find(j):   # different dedup groups → unmerged
                unmerged_pairs.append((norm_name, i, j))
    if len(unmerged_pairs) >= 200:   # enough candidates collected
        break

print(f"Found {len(unmerged_pairs)} same-name unmerged pairs (showing first 10)\n")


# ── Print 10 examples side by side ───────────────────────────────────────────

def why_not_merged(ri, rj) -> list[str]:
    """List every criterion that failed between two listings."""
    reasons = []
    lat_i, lon_i = ri.get("latitude"), ri.get("longitude")
    lat_j, lon_j = rj.get("latitude"), rj.get("longitude")

    loc_i = (ri.get("locality") or "").strip().lower()
    loc_j = (rj.get("locality") or "").strip().lower()
    if loc_i != loc_j:
        reasons.append(f"locality differs ({loc_i!r} vs {loc_j!r})")
    if ri.get("floor") != rj.get("floor"):
        reasons.append(f"floor differs ({ri.get('floor')} vs {rj.get('floor')})")
    if ri.get("bedroom") != rj.get("bedroom"):
        reasons.append(f"bedroom differs ({ri.get('bedroom')} vs {rj.get('bedroom')})")
    if lat_i is not None and lat_j is not None:
        d = haversine_m(lat_i, lon_i, lat_j, lon_j)
        if d > COORD_DIST_M:
            reasons.append(f"distance {d:,.1f} m > 30 m")
    else:
        reasons.append("missing coords")
    if not areas_within_pct(ri.get("carpet_area"), rj.get("carpet_area")):
        reasons.append(f"carpet_area diff > 5% "
                       f"({ri.get('carpet_area')} vs {rj.get('carpet_area')})")
    if not areas_within_pct(ri.get("super_built_up_area"), rj.get("super_built_up_area")):
        reasons.append(f"super_builtup diff > 5% "
                       f"({ri.get('super_built_up_area')} vs {rj.get('super_built_up_area')})")
    return reasons


print("=" * 72)
print("10 SAME-NAME PAIRS THAT WERE NOT MERGED")
print("=" * 72)

shown = 0
for norm_name, i, j in unmerged_pairs:
    if shown >= 10:
        break
    ri, rj = listings[i], listings[j]

    lat_i, lon_i = ri.get("latitude"), ri.get("longitude")
    lat_j, lon_j = rj.get("latitude"), rj.get("longitude")
    if lat_i and lat_j:
        dist_str = f"{haversine_m(lat_i, lon_i, lat_j, lon_j):,.1f} m"
    else:
        dist_str = "n/a"

    reasons = why_not_merged(ri, rj)

    print(f"\nPair {shown+1}  —  normalised name: \"{norm_name}\"")
    print(f"  {'Field':<22} {'Listing A':<30} {'Listing B'}")
    print(f"  {'-'*22} {'-'*30} {'-'*30}")
    for field in ["listing_id", "apartment_name", "website",
                  "floor", "bedroom", "locality",
                  "latitude", "longitude",
                  "carpet_area", "super_built_up_area", "price"]:
        va = str(ri.get(field, "—"))
        vb = str(rj.get(field, "—"))
        print(f"  {field:<22} {va:<30} {vb}")
    print(f"  {'distance apart':<22} {dist_str}")
    print(f"  WHY NOT MERGED:")
    for r in reasons:
        print(f"    ✗ {r}")
    shown += 1

print()
