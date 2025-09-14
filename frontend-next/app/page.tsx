import dynamic from "next/dynamic";
import styles from "./page.module.css";

const SearchClient = dynamic(() => import("../components/SearchClient"), {
  ssr: false,
});

export default function Home() {
  return (
    <main className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>AISearch Next</h1>
        <p className={styles.subtitle}>
          Professional Next.js frontend scaffold with Tailwind.
        </p>
        <div className={styles.searchArea}>
          <SearchClient />
        </div>
      </div>
    </main>
  );
}
