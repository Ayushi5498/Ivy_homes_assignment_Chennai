import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { loginApi } from '../api/client'
import Logo from '../components/Logo'
import styles from './Login.module.css'

export default function Login() {
    const { login } = useAuth()
    const navigate = useNavigate()

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        setLoading(true)
        try {
            const data = await loginApi(email, password)
            login(data.access_token, email)
            navigate('/')
        } catch (err) {
            setError(err.message || 'Login failed. Please check your credentials.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className={styles.page}>
            {/* Background city skyline SVG */}
            <svg className={styles.skyline} viewBox="0 0 1440 320" preserveAspectRatio="none"
                xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <defs>
                    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#C8673A" stopOpacity="0.12" />
                        <stop offset="100%" stopColor="#1A6B72" stopOpacity="0.08" />
                    </linearGradient>
                </defs>
                {/* Sea / horizon band */}
                <rect x="0" y="260" width="1440" height="60" fill="#1A6B72" opacity="0.07" />
                {/* Building silhouettes — abstract Chennai skyline */}
                <g fill="#2D3561" opacity="0.08">
                    <rect x="40" y="180" width="40" height="140" />
                    <rect x="55" y="160" width="12" height="20" />
                    <rect x="100" y="200" width="60" height="120" />
                    <rect x="170" y="150" width="50" height="170" />
                    <rect x="180" y="130" width="14" height="22" />
                    <rect x="230" y="190" width="35" height="130" />
                    <rect x="275" y="170" width="70" height="150" />
                    <rect x="290" y="148" width="16" height="24" />
                    <rect x="355" y="210" width="45" height="110" />
                    <rect x="410" y="165" width="55" height="155" />
                    <rect x="425" y="140" width="18" height="28" />
                    <rect x="475" y="185" width="40" height="135" />
                    <rect x="525" y="155" width="65" height="165" />
                    <rect x="540" y="135" width="14" height="22" />
                    <rect x="600" y="195" width="50" height="125" />
                    <rect x="660" y="170" width="45" height="150" />
                    <rect x="715" y="185" width="60" height="135" />
                    <rect x="730" y="162" width="16" height="25" />
                    <rect x="785" y="175" width="40" height="145" />
                    <rect x="835" y="155" width="55" height="165" />
                    <rect x="850" y="132" width="14" height="24" />
                    <rect x="900" y="195" width="50" height="125" />
                    <rect x="960" y="160" width="70" height="160" />
                    <rect x="978" y="138" width="18" height="24" />
                    <rect x="1040" y="180" width="45" height="140" />
                    <rect x="1095" y="165" width="60" height="155" />
                    <rect x="1110" y="142" width="16" height="25" />
                    <rect x="1165" y="190" width="50" height="130" />
                    <rect x="1225" y="170" width="55" height="150" />
                    <rect x="1240" y="148" width="14" height="24" />
                    <rect x="1290" y="185" width="45" height="135" />
                    <rect x="1345" y="175" width="60" height="145" />
                    <rect x="1360" y="150" width="16" height="28" />
                </g>
                {/* Warm glow overlay */}
                <rect x="0" y="0" width="1440" height="320" fill="url(#skyGrad)" />
            </svg>

            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <Logo size="lg" />
                    <p className={styles.tagline}>Chennai's finest properties, curated for you.</p>
                </div>

                <form className={styles.form} onSubmit={handleSubmit} noValidate>
                    <div className={styles.field}>
                        <label htmlFor="email">Email address</label>
                        <input
                            id="email"
                            type="email"
                            autoComplete="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className={styles.field}>
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            autoComplete="current-password"
                            placeholder="••••••••"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                            disabled={loading}
                        />
                    </div>

                    {error && <p className={styles.error} role="alert">{error}</p>}

                    <button className={styles.btn} type="submit" disabled={loading}>
                        {loading ? 'Signing in…' : 'Sign in'}
                    </button>
                </form>

                <p className={styles.hint}>
                    Demo accounts: <code>demo1@ivy.homes</code> — <code>demo2@ivy.homes</code> — <code>demo3@ivy.homes</code>
                    <br />Password: <code>e478e79361</code>
                </p>
            </div>
        </div>
    )
}
