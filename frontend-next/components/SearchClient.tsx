"use client";
import React, { useRef, useState, useEffect } from "react";
import SearchForm from "./SearchForm";
import ResultsList from "./ResultsList";
import styles from "./SearchClient.module.css";

type RecogType = {
  start: () => void;
  stop: () => void;
  onresult?: (ev: any) => void;
  onend?: () => void;
  onerror?: (err: any) => void;
  interimResults?: boolean;
  lang?: string;
};

export default function SearchClient() {
  const [results, setResults] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [listening, setListening] = useState(false);
  const [convoActive, setConvoActive] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const recogRef = useRef<RecogType | null>(null);

  const onSearch = async (q: string) => {
    setResults([]);
    try {
      const res = await fetch("/api/proxy", {
        method: "POST",
        body: JSON.stringify({ query: q }),
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch (e) {
      setResults([]);
    }
  };

  useEffect(() => {
    // Feature detect SpeechRecognition
    const SpeechRecognitionCtor =
      (window as any).webkitSpeechRecognition ||
      (window as any).SpeechRecognition;
    if (!SpeechRecognitionCtor) {
      recogRef.current = null;
      return;
    }

    const r: RecogType = new SpeechRecognitionCtor();
    r.interimResults = true;
    r.lang = "en-US";

    r.onresult = (ev: any) => {
      // build interim + final transcript
      let interim = "";
      let finalTranscript = "";
      for (let i = 0; i < ev.results.length; i++) {
        const res = ev.results[i];
        if (res.isFinal) finalTranscript += res[0].transcript;
        else interim += res[0].transcript;
      }
      const combined = (finalTranscript + " " + interim).trim();
      setQuery(combined);
      // if there's a final transcript, trigger a search automatically
      if (finalTranscript.trim()) {
        onSearch(combined);
      }
    };

    r.onend = () => {
      setListening(false);
    };

    r.onerror = (err: any) => {
      console.warn("SpeechRecognition error", err);
      setListening(false);
    };

    recogRef.current = r;

    return () => {
      try {
        if (recogRef.current) recogRef.current.stop();
      } catch (e) {
        /* ignore */
      }
      recogRef.current = null;
    };
  }, []);

  const toggleListen = () => {
    if (!recogRef.current) return;
    if (listening) {
      recogRef.current.stop();
      setListening(false);
    } else {
      recogRef.current.start();
      setListening(true);
      // ensure input focused
      inputRef.current && inputRef.current.focus();
    }
  };

  const startConvo = () => {
    setConvoActive(true);
    // focus input so mic results are visible
    setTimeout(() => inputRef.current && inputRef.current.focus(), 50);
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.controls}>
        {!convoActive ? (
          <button
            className={styles.startBtn}
            onClick={startConvo}
            aria-label="Start conversation"
          >
            Start Conversation
          </button>
        ) : (
          <div className={styles.micRow}>
            <div className={styles.micWrap}>
              <button
                className={
                  listening
                    ? `${styles.micButton} ${styles.active}`
                    : styles.micButton
                }
                onClick={toggleListen}
                aria-pressed={listening}
                aria-label="Toggle microphone"
                type="button"
              >
                {listening ? "🎙️" : "🎤"}
              </button>
            </div>
            <div className={styles.hint}>
              {listening ? "Listening..." : "Click mic to speak"}
            </div>
          </div>
        )}
      </div>

      <SearchForm
        onSearch={onSearch}
        value={query}
        onChange={setQuery}
        inputRef={inputRef}
      />

      <div className={styles.results}>
        <ResultsList results={results} />
      </div>
    </div>
  );
}
