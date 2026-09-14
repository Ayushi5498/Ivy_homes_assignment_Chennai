import styles from './Logo.module.css'

export default function Logo({ size = 'md' }) {
    return (
        <div className={`${styles.logo} ${styles[size]}`}>
            {/* Small ivy leaf SVG */}
            <svg
                className={styles.leaf}
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
            >
                {/* Stem */}
                <path d="M12 22 Q12 14 12 8" stroke="currentColor" strokeWidth="1.5"
                    strokeLinecap="round" />
                {/* Left leaf */}
                <path d="M12 14 Q6 12 5 6 Q10 7 12 14Z"
                    fill="currentColor" opacity="0.85" />
                {/* Right leaf */}
                <path d="M12 10 Q18 8 19 2 Q14 4 12 10Z"
                    fill="currentColor" />
            </svg>
            <span className={styles.wordmark}>
                <span className={styles.ivy}>Ivy</span>
                <span className={styles.homes}> Homes</span>
            </span>
        </div>
    )
}
