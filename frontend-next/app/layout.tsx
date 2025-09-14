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
    <html lang="en">
      <head>
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
            ["--bg" as any]: "#f8fafc",
            ["--card" as any]: "#ffffff",
            ["--muted" as any]: "#6b7280",
            ["--accent" as any]: "#2563eb",
            ["--radius" as any]: "12px",
          } as React.CSSProperties
        }
      >
        {children}
      </body>
    </html>
  );
}
