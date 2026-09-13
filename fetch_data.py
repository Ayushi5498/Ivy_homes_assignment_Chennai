# fetch_data.py
#
# HOW TO RUN:
#   1. Make sure you have the 'requests' library installed:
#        pip install requests
#   2. Run the script:
#        python fetch_data.py
#
#   Output files will be created in the same directory:
#       listings_all.json, rentals_all.json, projects_all.json

import json
import requests

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_URL   = "https://solve.ivy.homes"
EMAIL      = "demo1@ivy.homes"
PASSWORD   = "e478e79361"
API_KEY    = "IVY26-C5048846CD4F"
PAGE_LIMIT = 200   # records per page

# Endpoints to collect, mapped to their output file names
ENDPOINTS = {
    "listings": "listings_all.json",
    "rentals":  "rentals_all.json",
    "projects": "projects_all.json",
}

# ─── Step 1: Login ────────────────────────────────────────────────────────────

def login() -> str:
    """POST /auth/login and return the access_token."""
    url = f"{BASE_URL}/auth/login"
    payload = {"email": EMAIL, "password": PASSWORD}
    # X-API-Key is required on the login request itself
    login_headers = {"X-API-Key": API_KEY}

    print("Logging in...")
    response = requests.post(url, json=payload, headers=login_headers)

    if response.status_code != 200:
        print(f"Login failed — status {response.status_code}")
        print(response.text)
        raise SystemExit(1)

    data = response.json()
    token = data.get("access_token")
    if not token:
        print("Login response did not contain 'access_token'.")
        print(json.dumps(data, indent=2))
        raise SystemExit(1)

    print("Login successful.\n")
    return token


# ─── Step 2: Fetch all pages for one endpoint ─────────────────────────────────

def fetch_all(endpoint: str, headers: dict) -> list:
    """
    Paginate through /v1/<endpoint> and return all collected results.

    The API uses offset-based pagination (limit + offset), NOT page numbers.
    It also returns a 'has_more' boolean that signals whether more records exist.

    Stops when:
      - has_more is False, OR
      - a page returns an empty results list
    """
    url = f"{BASE_URL}/v1/{endpoint}"
    all_results = []
    offset = 0
    page_num = 1  # just for human-readable progress output

    while True:
        params = {"limit": PAGE_LIMIT, "offset": offset}
        response = requests.get(url, headers=headers, params=params)

        # Handle non-200 responses gracefully
        if response.status_code != 200:
            print(f"\nError fetching {endpoint} (offset {offset}) — "
                  f"status {response.status_code}")
            print(response.text)
            raise SystemExit(1)

        data = response.json()
        total    = data.get("total", 0)
        results  = data.get("results", [])
        has_more = data.get("has_more", False)

        if not results:
            # No records returned — we're done
            print(f"  Page {page_num} returned no results; stopping.")
            break

        # Collect this batch first, then decide whether to continue
        all_results.extend(results)
        print(f"  Fetched page {page_num} of {endpoint} "
              f"({len(all_results)}/{total} records)")

        # Stop only after collecting — has_more=False on the last real page
        # means this was the final batch, so we're done
        if not has_more:
            break

        offset   += len(results)   # advance by actual records returned, not PAGE_LIMIT
        page_num += 1

    return all_results


# ─── Step 3: Save results to a JSON file ──────────────────────────────────────

def save_json(data: list, filename: str) -> None:
    """Write a list of records to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(data)} records → {filename}\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # 1. Authenticate
    access_token = login()

    # 2. Build the headers that every subsequent request must include
    headers = {
        "X-API-Key":     API_KEY,
        "Authorization": f"Bearer {access_token}",
    }

    # 3. Collect data from each endpoint and save it
    summary = {}
    for endpoint, filename in ENDPOINTS.items():
        print(f"── Fetching {endpoint} ──────────────────────────")
        records = fetch_all(endpoint, headers)
        save_json(records, filename)
        summary[endpoint] = len(records)

    # 4. Print final summary
    print("════════════════════════════════════════════════")
    print("Summary — total records saved:")
    for endpoint, count in summary.items():
        print(f"  {endpoint:<12} {count:>6} records")
    print("════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
