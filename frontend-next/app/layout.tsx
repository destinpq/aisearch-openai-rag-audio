import React from "react";
import styles from "./layout.module.css";

export const metadata = {
  title: "AISearch Next",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.svg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body
        className={styles.body}
        style={
          {
            // set CSS variables inline so component CSS modules can use them
            ["--bg" as any]: "#f7fafc",
            ["--card" as any]: "#ffffff",
            ["--muted" as any]: "#6b7280",
            ["--accent" as any]: "#6d28d9",
            ["--radius" as any]: "12px",
            ["--text-primary" as any]: "#0f172a",
            ["--text-secondary" as any]: "#374151",
          } as React.CSSProperties
        }
      >
        {children}
      </body>
    </html>
  );
}
