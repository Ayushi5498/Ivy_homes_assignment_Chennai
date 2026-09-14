import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Listings from './pages/Listings'
import ListingDetail from './pages/ListingDetail'
import PlaceholderPage from './pages/PlaceholderPage'

function AuthLayout() {
    return (
        <>
            <Navbar />
            <Routes>
                <Route index element={<Navigate to="/listings" replace />} />
                <Route path="listings" element={<Listings />} />
                <Route path="listings/:id" element={<ListingDetail />} />
                <Route path="rentals" element={<PlaceholderPage title="Rentals" />} />
                <Route path="projects" element={<PlaceholderPage title="Projects" />} />
                <Route path="favourites" element={<PlaceholderPage title="Favourites" />} />
                <Route path="insights" element={<PlaceholderPage title="Insights" />} />
                <Route path="*" element={<Navigate to="/listings" replace />} />
            </Routes>
        </>
    )
}

// Guard: redirect unauthenticated users to /login
function RequireAuth({ children }) {
    const { accessToken } = useAuth()
    return accessToken ? children : <Navigate to="/login" replace />
}

function AppRoutes() {
    const { accessToken } = useAuth()
    return (
        <Routes>
            <Route
                path="/login"
                element={accessToken ? <Navigate to="/" replace /> : <Login />}
            />
            <Route
                path="/*"
                element={
                    <RequireAuth>
                        <AuthLayout />
                    </RequireAuth>
                }
            />
        </Routes>
    )
}

export default function App() {
    return (
        <AuthProvider>
            <AppRoutes />
        </AuthProvider>
    )
}
