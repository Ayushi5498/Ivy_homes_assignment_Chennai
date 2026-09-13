import requests, json

BASE_URL = "https://solve.ivy.homes"
API_KEY  = "IVY26-C5048846CD4F"

r = requests.post(f"{BASE_URL}/auth/login",
                  json={"email": "demo1@ivy.homes", "password": "e478e79361"},
                  headers={"X-API-Key": API_KEY})
token = r.json()["access_token"]
headers = {"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"}

# Check the last page that returned results and the one after it
for offset in [1000, 1050, 1100]:
    resp = requests.get(f"{BASE_URL}/v1/listings", headers=headers,
                        params={"limit": 50, "offset": offset})
    d = resp.json()
    first_id = d["results"][0].get("listing_id") if d["results"] else None
    print(f"offset={offset}  total={d.get('total')}  count={d.get('count')}  "
          f"has_more={d.get('has_more')}  results={len(d['results'])}  first_id={first_id}")
