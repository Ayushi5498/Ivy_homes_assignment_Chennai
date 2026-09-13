import requests

BASE_URL = "https://solve.ivy.homes"
API_KEY  = "IVY26-C5048846CD4F"

r = requests.post(f"{BASE_URL}/auth/login",
    json={"email": "demo1@ivy.homes", "password": "e478e79361"},
    headers={"X-API-Key": API_KEY})
token = r.json()["access_token"]
headers = {"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"}

print(f"{'offset':<8} {'total':<8} {'count':<8} {'has_more':<10} {'results_returned':<18} first_id  ->  last_id")
print("-" * 90)

# Fine-grained scan from 4050 to 5000 in steps of 50
for offset in range(4050, 5050, 50):
    resp = requests.get(f"{BASE_URL}/v1/listings", headers=headers,
                        params={"offset": offset, "limit": 50})
    d = resp.json()
    results = d["results"]
    first_id = results[0].get("listing_id")  if results else "-"
    last_id  = results[-1].get("listing_id") if results else "-"
    print(f"{offset:<8} {d['total']:<8} {d['count']:<8} {str(d['has_more']):<10} {len(results):<18} {first_id}  ->  {last_id}")
    if not results:
        break
