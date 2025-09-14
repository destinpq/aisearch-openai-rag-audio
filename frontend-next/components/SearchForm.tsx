"use client";
import React, { useRef, ForwardedRef } from "react";
import styles from "./SearchForm.module.css";

export default function SearchForm({
  onSearch,
  value = "",
  onChange,
  inputRef,
}: {
  onSearch: (q: string) => void;
  value?: string;
  onChange?: (v: string) => void;
  inputRef?: ForwardedRef<HTMLInputElement> | null;
}) {
  const internalRef = useRef<HTMLInputElement | null>(null);
  const ref = (inputRef as any) || internalRef;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSearch(value || "");
      }}
      className={styles.form}
    >
      <input
        ref={ref as any}
        className={styles.input}
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        placeholder="Search your documents"
        aria-label="Search"
      />
      <button type="submit" className={styles.button} aria-label="Search">
        Search
      </button>
    </form>
  );
}
