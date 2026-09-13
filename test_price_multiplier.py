import json, statistics

with open("listings_all.json") as f: listings = json.load(f)
with open("submission.json") as f: sub = json.load(f)

orig = set(sub["answers"]["corrupt_listing_ids"])
new_ids = ["100-4001484","100-4001961","DWE-4000745","MAG-4000870",
           "MAG-4001467","MAG-4002092","SQU-4001342","ZER-4002683"]
by_id = {r["listing_id"]: r for r in listings}

ref = [r["price"]/r["carpet_area"] for r in listings
       if r["listing_id"] not in orig
       and r.get("price") and r.get("carpet_area")
       and 3000 <= r["price"]/r["carpet_area"] <= 25000]
med = statistics.median(ref)
print(f"Reference median ppsf: {med:,.0f}\n")

for mult in [100, 1000]:
    print(f"-- multiplier ×{mult} --")
    for lid in new_ids:
        r = by_id[lid]
        p = r["price"]; c = r["carpet_area"]
        ppsf = p * mult / c
        ok = "✓ in range" if med * 0.5 <= ppsf <= med * 2 else "✗ out of range"
        print(f"  {lid:<18}  raw={p:>8,}  ×{mult}={p*mult:>12,}  ppsf={ppsf:>7.0f}  {ok}")
    print()
