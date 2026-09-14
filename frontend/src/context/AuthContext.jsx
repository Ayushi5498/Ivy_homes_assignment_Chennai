import { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)

const STORAGE_KEY = 'ivy_access_token'
const EMAIL_KEY = 'ivy_user_email'

export function AuthProvider({ children }) {
    const [accessToken, setAccessToken] = useState(
        () => localStorage.getItem(STORAGE_KEY) || null
    )
    const [userEmail, setUserEmail] = useState(
        () => localStorage.getItem(EMAIL_KEY) || null
    )

    const login = useCallback((token, email) => {
        localStorage.setItem(STORAGE_KEY, token)
        localStorage.setItem(EMAIL_KEY, email)
        setAccessToken(token)
        setUserEmail(email)
    }, [])

    const logout = useCallback(() => {
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem(EMAIL_KEY)
        setAccessToken(null)
        setUserEmail(null)
    }, [])

    return (
        <AuthContext.Provider value={{ accessToken, userEmail, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
    return ctx
}
