"use client";
import React from "react";
import styles from "./ResultsList.module.css";

export default function ResultsList({
  results,
  connState,
}: {
  results: any[];
  connState?: "idle" | "connecting" | "open" | "closed";
}) {
  if (!results || results.length === 0)
    return <div className={styles.empty}>No results</div>;
  return (
    <div>
      {/* Show all answer texts in a big readable way */}
      <div
        style={{
          fontSize: "1.5rem",
          fontWeight: 600,
          margin: "24px 0",
          color: "#1e293b",
          wordBreak: "break-word",
          whiteSpace: "pre-line",
        }}
      >
        {results.map((r, i) => (
          <div key={i} style={{ marginBottom: 24 }}>
            {typeof r === "string"
              ? r
              : r && (r.text || r.content)
              ? r.text || r.content
              : JSON.stringify(r)}
            {i === results.length - 1 && connState === "open" && (
              <span className={styles.typingCursor} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
