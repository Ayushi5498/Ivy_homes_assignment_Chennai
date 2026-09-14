import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Logo from './Logo'
import styles from './Navbar.module.css'

const NAV_LINKS = [
    { to: '/listings', label: 'Listings' },
    { to: '/rentals', label: 'Rentals' },
    { to: '/projects', label: 'Projects' },
    { to: '/favourites', label: 'Favourites' },
    { to: '/insights', label: 'Insights' },
]

export default function Navbar() {
    const { userEmail, logout } = useAuth()

    return (
        <header className={styles.header}>
            <nav className={styles.nav}>
                <NavLink to="/" className={styles.brand} aria-label="Home">
                    <Logo size="sm" />
                </NavLink>

                <ul className={styles.links}>
                    {NAV_LINKS.map(({ to, label }) => (
                        <li key={to}>
                            <NavLink
                                to={to}
                                className={({ isActive }) =>
                                    `${styles.link} ${isActive ? styles.active : ''}`
                                }
                            >
                                {label}
                            </NavLink>
                        </li>
                    ))}
                </ul>

                <div className={styles.user}>
                    <span className={styles.email} title={userEmail}>{userEmail}</span>
                    <button className={styles.logoutBtn} onClick={logout}>
                        Sign out
                    </button>
                </div>
            </nav>
        </header>
    )
}
