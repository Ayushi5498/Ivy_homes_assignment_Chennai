const BASE_URL = 'https://solve.ivy.homes'
const API_KEY = 'IVY26-C5048846CD4F'

export async function loginApi(email, password) {
    const res = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY,
        },
        body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
        const err = await res.text()
        throw new Error(err || `Login failed (${res.status})`)
    }
    return res.json() // { access_token, refresh_token, ... }
}

export function authHeaders(token) {
    return {
        'X-API-Key': API_KEY,
        'Authorization': `Bearer ${token}`,
    }
}

/**
 * Fetch one page of listings.
 * offset-based; stops when has_more=false or results=[].
 */
export async function fetchListingsPage(token, offset = 0, limit = 50) {
    const params = new URLSearchParams({ limit, offset })
    const res = await fetch(`${BASE_URL}/v1/listings?${params}`, {
        headers: authHeaders(token),
    })
    if (!res.ok) throw new Error(`Listings fetch failed (${res.status})`)
    return res.json()
}

export async function fetchListingById(token, id) {
    const res = await fetch(`${BASE_URL}/v1/listings/${encodeURIComponent(id)}`, {
        headers: authHeaders(token),
    })
    if (res.status === 404) throw new Error('NOT_FOUND')
    if (!res.ok) throw new Error(`Failed to load listing (${res.status})`)
    return res.json()
}

// ── Saved / Favourites (/v1/saved) ────────────────────────────────────────────

export async function fetchSaved(token) {
    const res = await fetch(`${BASE_URL}/v1/saved`, { headers: authHeaders(token) })
    if (!res.ok) throw new Error(`Failed to load saved listings (${res.status})`)
    return res.json()  // { count, results: [...listing objects] }
}

export async function addSaved(token, listingId) {
    const res = await fetch(`${BASE_URL}/v1/saved`, {
        method: 'POST',
        headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
        body: JSON.stringify({ listing_id: listingId }),
    })
    if (!res.ok) throw new Error(`Failed to save listing (${res.status})`)
    return res.json()  // { ok, listing_id, saved_count }
}

export async function removeSaved(token, listingId) {
    const res = await fetch(
        `${BASE_URL}/v1/saved/${encodeURIComponent(listingId)}`,
        { method: 'DELETE', headers: authHeaders(token) }
    )
    if (!res.ok) throw new Error(`Failed to remove saved listing (${res.status})`)
    return res.json()  // { ok, listing_id, saved_count }
}

// ── Rentals ───────────────────────────────────────────────────────────────────

export async function fetchRentalsPage(token, offset = 0, limit = 50) {
    const params = new URLSearchParams({ limit, offset })
    const res = await fetch(`${BASE_URL}/v1/rentals?${params}`, {
        headers: authHeaders(token),
    })
    if (!res.ok) throw new Error(`Rentals fetch failed (${res.status})`)
    return res.json()
}

// ── Projects ──────────────────────────────────────────────────────────────────

export async function fetchProjectsPage(token, offset = 0, limit = 50) {
    const params = new URLSearchParams({ limit, offset })
    const res = await fetch(`${BASE_URL}/v1/projects?${params}`, {
        headers: authHeaders(token),
    })
    if (!res.ok) throw new Error(`Projects fetch failed (${res.status})`)
    return res.json()
}

/**
 * Normalise project price_max / price_min to full rupees.
 * Values < 4   → crores  (× 1,00,00,000)
 * Values >= 50 → lakhs   (× 1,00,000)
 * Gap 4–49 has zero entries, so this covers all real data.
 */
export function normProjectPrice(val) {
    if (val == null) return null
    return val < 10 ? Math.round(val * 1_00_00_000) : Math.round(val * 1_00_000)
}
