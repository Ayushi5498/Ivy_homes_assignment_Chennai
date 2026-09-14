import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { FavouritesProvider } from './context/FavouritesContext'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Listings from './pages/Listings'
import ListingDetail from './pages/ListingDetail'
import Rentals from './pages/Rentals'
import Projects from './pages/Projects'
import Favourites from './pages/Favourites'
import Insights from './pages/Insights'
import PlaceholderPage from './pages/PlaceholderPage'

function AuthLayout() {
    return (
        <>
            <Navbar />
            <Routes>
                <Route index element={<Navigate to="/listings" replace />} />
                <Route path="listings" element={<Listings />} />
                <Route path="listings/:id" element={<ListingDetail />} />
                <Route path="rentals" element={<Rentals />} />
                <Route path="projects" element={<Projects />} />
                <Route path="favourites" element={<Favourites />} />
                <Route path="insights" element={<Insights />} />
                <Route path="*" element={<Navigate to="/listings" replace />} />
            </Routes>
        </>
    )
}

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
                        <FavouritesProvider>
                            <AuthLayout />
                        </FavouritesProvider>
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
