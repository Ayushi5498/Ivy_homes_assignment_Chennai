import requests

API_KEY = "IVY26-C5048846CD4F"
BASE_URL = "https://solve.ivy.homes"

# Step 1: Get auth token
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json={"email": "demo1@ivy.homes", "password": "e478e79361"}
)
print(f"Login status: {login_resp.status_code}")
token = login_resp.json().get("token") or login_resp.json().get("access_token")
print(f"Token: {token[:30]}..." if token else f"Login response keys: {list(login_resp.json().keys())}")

headers = {
    "X-API-Key": API_KEY,
    "Authorization": f"Bearer {token}"
}

# Step 2: Try both paths
for path in ["/v1/listings/MAG-4001518", "/v1/listing/MAG-4001518"]:
    r = requests.get(f"{BASE_URL}{path}", headers=headers)
    print(f"\nGET {path}")
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Top-level keys: {list(data.keys())}")
    else:
        print(f"  Response: {r.text[:200]}")
