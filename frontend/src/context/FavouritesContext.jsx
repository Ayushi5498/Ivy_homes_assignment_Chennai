import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { fetchSaved, addSaved, removeSaved } from '../api/client'
import { useAuth } from './AuthContext'

const FavouritesContext = createContext(null)

export function FavouritesProvider({ children }) {
    const { accessToken } = useAuth()

    // Full listing objects returned by GET /v1/saved
    const [savedListings, setSavedListings] = useState([])
    const [loading, setLoading] = useState(false)

    // Derived Set of IDs for O(1) lookup
    const savedIds = new Set(savedListings.map(r => r.listing_id))

    // Load on mount / token change
    useEffect(() => {
        if (!accessToken) { setSavedListings([]); return }
        setLoading(true)
        fetchSaved(accessToken)
            .then(data => setSavedListings(data.results ?? []))
            .catch(() => { })
            .finally(() => setLoading(false))
    }, [accessToken])

    const isSaved = useCallback(id => savedIds.has(id), [savedListings]) // eslint-disable-line

    const toggleSaved = useCallback(async (listingId) => {
        if (!accessToken) return
        const wasSaved = savedIds.has(listingId)

        // Optimistic update
        if (wasSaved) {
            setSavedListings(prev => prev.filter(r => r.listing_id !== listingId))
        }
        // For add, we don't have the full object yet — API returns it on GET
        // so we just call the API and then re-fetch to get full object
        try {
            if (wasSaved) {
                await removeSaved(accessToken, listingId)
            } else {
                await addSaved(accessToken, listingId)
                // Re-fetch to get the full listing object back
                const data = await fetchSaved(accessToken)
                setSavedListings(data.results ?? [])
            }
        } catch {
            // Rollback: re-fetch authoritative state
            fetchSaved(accessToken)
                .then(data => setSavedListings(data.results ?? []))
                .catch(() => { })
        }
    }, [accessToken, savedListings]) // eslint-disable-line

    return (
        <FavouritesContext.Provider value={{ savedListings, savedIds, loading, isSaved, toggleSaved }}>
            {children}
        </FavouritesContext.Provider>
    )
}

export function useFavourites() {
    const ctx = useContext(FavouritesContext)
    if (!ctx) throw new Error('useFavourites must be used inside FavouritesProvider')
    return ctx
}
