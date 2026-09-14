import styles from './PlaceholderPage.module.css'

export default function PlaceholderPage({ title }) {
    return (
        <main className={styles.page}>
            <div className={styles.pill}>{title}</div>
            <h1 className={styles.title}>{title}</h1>
            <p className={styles.sub}>This page is coming soon.</p>
        </main>
    )
}
