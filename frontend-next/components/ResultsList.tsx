"use client";
import React from "react";
import styles from "./ResultsList.module.css";

export default function ResultsList({ results }: { results: any[] }) {
  if (!results || results.length === 0)
    return <div className={styles.empty}>No results</div>;
  return (
    <div className={styles.list}>
      {results.map((r, i) => (
        <div key={i} className={styles.card}>
          <div className={styles.title}>{r.title || r.filename}</div>
          <div className={styles.text}>{r.text || r.content}</div>
        </div>
      ))}
    </div>
  );
}
