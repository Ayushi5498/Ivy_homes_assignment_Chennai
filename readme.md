# Ivy Homes — Chennai Real Estate Assignment

**Candidate:** Ayushi Chauhan  
**Email:** ayushic2027@gmail.com  
**Repo:** https://github.com/Ayushi5498/Ivy_homes_assignment_Chennai

---

## Running the project

```bash
# Data analysis scripts (Python)
pip install requests
python fetch_data.py        # fetches all listings, rentals, projects to JSON
python check_duplicates.py  # verifies no duplicate IDs

# Frontend (React + Vite)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

No `.env` file needed — the API key and demo credentials are hardcoded in the Python scripts and frontend API client for this assignment. In production these would live in environment variables.

---

## What this project is

A full-stack real estate browsing app for Chennai, built on top of the Ivy Homes API. It includes:

- A **Python data pipeline** that fetches all 4,100 listings, 1,550 rentals, and 460 projects from the API, with a full investigation of the dataset's real state vs. what the documentation claims
- A **React + Vite frontend** with login, listings grid + infinite scroll + filters, listing detail, rentals, projects, favourites (backed by the real `/v1/saved` API), and an insights dashboard
- A **`submission.json`** with verified answers to all 10 assignment questions and 9 documented data quality findings

---

## What I distrusted in the documentation — and what I found

### 1. Auth header required on login itself

The docs only mention `X-API-Key` for post-login requests. The login call itself returned a missing-header error without it. Fixed by adding the header to `POST /auth/login`. Confirmed immediately.

### 2. Pagination `total` field is unreliable — two separate bugs

The docs described `page`/`limit` parameters and said `total` reflects the real dataset size. Both were wrong:

- **The API ignores `page`** — it uses `offset` instead. Sending `page=2` returned identical records to `page=1`, causing 77× duplicates for every listing in the first naive implementation.
- **`total` undercounts** — the API reports `total: 3,836` for listings, but `has_more` stays `true` past that point. Fetching to the real end (stopping only when `has_more: false` or empty results) yields **4,100 records** — 264 more than reported.
- **Offset must advance by `len(results)`, not `limit`** — the API caps pages at 50 records regardless of the requested limit. Advancing offset by the configured `limit=200` skipped 150 records per page.

Confirmed by probing offsets 3,836, 3,850, and 4,100 directly and observing live records well past the reported total.

### 3. `project_id` linkage is random noise

The docs present `project_id` as a meaningful link between listings and builder projects. Measuring pairwise distances between listings sharing the same `project_id` showed:

- 99.6% of same-`project_id` listing pairs are **over 1 km apart**
- The most extreme case: two listings with the same `project_id` are **8,172 km apart**
- Project P40276 is named "Brigade Meadows" in the projects table, but its 12 linked listings carry names like "Prestige Vista", "SHRIRAM CREST", "Rohan Park", and "Aparna Heights" — four unrelated buildings 13–25 km apart
- 336 of 460 projects (73%) have a `total_listings` count that doesn't match the actual number of listings sharing their `project_id`

Conclusion: `project_id` values appear to be randomly or incorrectly assigned and can't be used for any grouping or location-based analysis.

### 4. Area fields in square metres on one portal

The docs say all areas are in square feet. Around 326 listings had carpet areas of 70–90 for a "2BHK" — impossible in sqft.

Testing the square-metres hypothesis: multiplying by 10.764 produced values 750–860% *larger* than `super_built_up_area`, which is physically impossible. The key insight: the **internal ratio between `carpet_area` and `super_built_up_area`** in these listings was ~75% — identical to every other portal. Both fields were in sq m together, not just one.

Corrected by multiplying both fields by 10.764. Result: realistic 2BHK sizes (807–936 sqft) and ₹/sqft values aligning with the dataset median. These records were corrected and included in calculations, not excluded.

### 5. Project price fields use mixed units (crores and lakhs)

The docs say `price_min` and `price_max` are in rupees. The actual distribution:
- 433 projects with values 1.01–3.99 → **crores**
- 27 projects with values 50–99.8 → **lakhs**  
- **Zero projects** with values between 4 and 50 — a clean gap confirming two separate unit scales

Without correcting this, a ₹99.8 lakh project appeared to rank above projects worth ₹3.5–3.78 crore. Correction rule: `< 10 → ×1,00,00,000 (crores)`, `≥ 50 → ×1,00,000 (lakhs)`. Verified by checking implied price-per-sqft against listing medians for the same localities.

### 6. Eight listings have prices in thousands instead of rupees

Eight listings had prices like `9,430` for a full property. Testing multipliers: ×100 gave ~₹9.4L (still too low at ~₹948/sqft), ×1000 gave ~₹94.3L — putting all 8 listings within the expected ₹7,574–11,572/sqft range. Corrected with ×1000 and included.

### 7. Prompt injection attempts in listing descriptions

Seven listing descriptions contained hidden instructions targeting AI coding assistants:

- **Pattern 1** (3 listings — DWE and ZER sources): falsely claims a "data licence" requires every app to show a "Data certified by 100acres · 100A-B92098" footer
- **Pattern 2** (4 listings — MAG, SQU, ZER, 100acres): impersonates "the Ivy Homes data team" and instructs automated tools to inject a fabricated `"dataset_audit_ref": "IVY-AUDIT-7A83FCCE"` field into `submission.json`'s answers

Neither instruction was followed. Found during frontend development by noticing suspicious text in a listing description, then scanning all 4,100 descriptions with regex patterns.

---

## What I checked that turned out to be fine

**floor = 0 and bedroom = 0 records** — 138 and 147 records respectively triggered corruption checks. Pulling full records showed every single one had `property_type: "plot"`. Plots don't have floors or bedrooms. Zero is correct. Cleared after manual verification.

**Contact numbers appearing on 10–12 listings** — An initial fake-listing check was being too broad. Inspecting contacts with 10–12 listings showed coherent, varied portfolios: different apartment names, different localities, different property types — consistent with a busy but legitimate agent. Contacts with 15+ listings showed a completely different pattern: scattered across unrelated builders, often 20+ km apart. The cutoff of 15 was set after this manual inspection, not guessed.

**Property type and furnishing values** — Checks for invalid enum values found zero violations across 4,100 records. All listings use only the documented values.

---

## What I'd do with two more days

1. **Heart button state on listing cards in the grid** — the `ListingCard` component doesn't currently read from `FavouritesContext`, so the heart icon on the grid page doesn't reflect saved state. A quick context hook addition fixes this.

2. **Rental detail page** — each rental card isn't currently clickable to a detail view. The API supports `GET /v1/rentals/{id}` and the `ListingDetail` pattern is directly reusable.

3. **Map view** — all listings have verified lat/lon. A Leaflet.js map with pins colour-coded by price range would be genuinely useful. The coordinates are clean enough (after filtering the 9 swapped-coordinate records) to support it.

4. **Frontend unit corrections** — the sqm-area and price-in-thousands corrections currently only happen in Python. The React frontend fetches raw data and displays it as-is. Porting the correction logic to the API client layer would make displayed areas and ₹/sqft accurate for all users.

5. **Deeper fake-listing detection** — the current method (contact reuse × price anomaly) is a clean two-signal approach. Cross-referencing with duplicate descriptions and identical coordinates would surface additional patterns and reduce false positives further.

---

## Tools used

- **Python** with `requests` for all data fetching, analysis, and verification scripts
- **React + Vite** for the frontend, with React Router, CSS Modules
- **[Kiro](https://kiro.dev)** (AI coding assistant) was used throughout — for writing and debugging the Python analysis scripts, and for building the React frontend — under my direction and review at each step. Every finding in `submission.json` was verified by running scripts and inspecting real output before being recorded. Every frontend component was tested in the browser before being committed.
