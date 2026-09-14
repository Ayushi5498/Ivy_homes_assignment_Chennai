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
