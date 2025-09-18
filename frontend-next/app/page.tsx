"use client";

import { useState } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [ttsText, setTtsText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleTTS = async () => {
    if (!ttsText.trim()) return;

    setIsLoading(true);
    try {
      const backendOrigin = "http://localhost:2355";
      const resp = await fetch(`${backendOrigin.replace(/\/$/, "")}/tts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: ttsText,
          lang: "auto",
        }),
      });

      if (!resp.ok) {
        throw new Error(`Server TTS failed: ${resp.status}`);
      }

      const audioBlob = await resp.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error:", error);
      alert(
        "Failed to generate speech. Please ensure the backend is running on localhost:2355."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>🎤 Text-to-Speech Generator</h1>
        <p className={styles.subtitle}>
          Enter your text below and let the magic happen!
        </p>
        <div className={styles.form}>
          <input
            type="text"
            value={ttsText}
            onChange={(e) => setTtsText(e.target.value)}
            placeholder="Type something awesome..."
            className={styles.input}
          />
          <button
            onClick={handleTTS}
            disabled={isLoading}
            className={`${styles.primaryBtn} ${
              isLoading ? styles.disabled : ""
            }`}
          >
            {isLoading ? "🔄 Generating..." : "🔊 Speak It!"}
          </button>
        </div>
      </div>
    </main>
  );
}
