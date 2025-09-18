"use client";
import React, { useRef, useState, useEffect, useCallback } from "react";
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
  // (onlyDemo detection handled later after hooks)
  const [results, setResults] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [listening, setListening] = useState(false);
  const [convoActive, setConvoActive] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const recogRef = useRef<RecogType | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [connState, setConnState] = useState<
    "idle" | "connecting" | "open" | "closed"
  >("idle");
  const retryRef = useRef(0);
  const MAX_RETRIES = 3;
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showHud, setShowHud] = useState(false);
  const [hudShrunk, setHudShrunk] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [launching, setLaunching] = useState(false);
  const [showLauncher, setShowLauncher] = useState(true);
  const [transliterateEnabled, setTransliterateEnabled] = useState(false);
  const [transliteration, setTransliteration] = useState("");
  const [applyTransliteration, setApplyTransliteration] = useState(false);
  const [transliterationLoading, setTransliterationLoading] = useState(false);
  const [autoApplyToQuery, setAutoApplyToQuery] = useState(false);
  const translitTimer = useRef<number | null>(null);
  const [textBoxContent, setTextBoxContent] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const utterRef = useRef<SpeechSynthesisUtterance | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const phraseBufferRef = useRef<string[]>([]);
  const originalWordsRef = useRef<string[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const mediaSourceRef = useRef<MediaSource | null>(null);
  const phraseTimerRef = useRef<number | null>(null);
  // voice / audio controls
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceUri, setSelectedVoiceUri] = useState<string | null>(null);
  const [rate, setRate] = useState<number>(1);
  const [pitch, setPitch] = useState<number>(1);
  const [volume, setVolume] = useState<number>(1);

  // Spoken text highlighting and state
  const [spokenText, setSpokenText] = useState<string>("");
  const [highlightWordIndex, setHighlightWordIndex] = useState<number | null>(
    null
  );

  // Demo edit-box + read button (hidden in UI but present in source)
  // A simple local text box and button that uses the Web Speech API to read the text aloud.
  const [editText, setEditText] = useState<string>("");

  const speakText = (t: string) => {
    if (!t) return;
    if (!(window as any).speechSynthesis) {
      console.warn("SpeechSynthesis not supported");
      return;
    }
    try {
      // cancel any ongoing utterances
      try {
        (window as any).speechSynthesis.cancel();
      } catch (e) {}
      const u = new SpeechSynthesisUtterance(t);
      u.rate = Number(rate) || 1;
      u.pitch = Number(pitch) || 1;
      u.volume = Number(volume) || 1;
      utterRef.current = u;
      (window as any).speechSynthesis.speak(u);
      u.onend = () => {
        if (utterRef.current === u) utterRef.current = null;
      };
    } catch (e) {
      console.warn("speakText failed", e);
    }
  };

  // (onlyDemo rendering will be handled just before the main return to avoid
  // violating the rules-of-hooks)
  const onlyDemo =
    typeof window !== "undefined" &&
    (new URLSearchParams(window.location.search).get("onlyDemo") === "1" ||
      new URLSearchParams(window.location.search).get("demo") === "1");
  const onSearch = async (text: string) => {
    console.log("onSearch:", text);
    // minimal behavior: show the query in results for dev/testing
    setResults([{ text }]);
  };

  const stopStream = () => {
    if (eventSourceRef.current) {
      try {
        eventSourceRef.current.close();
      } catch (e) {
        /* ignore */
      }
      eventSourceRef.current = null;
      setConnState("closed");
    }
  };

  // Fallback: fetch server-generated MP3 via /tts and play it in an <audio> element.
  const playServerTTS = async () => {
    const text = textBoxContent.trim();
    if (!text) return;
    try {
      const backendOrigin =
        (process.env.NEXT_PUBLIC_BACKEND_ORIGIN as string) ||
        "http://localhost:2355";
      console.log("Requesting server TTS for text:", text);
      const resp = await fetch(`${backendOrigin.replace(/\/$/, "")}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "audio/mpeg" },
        body: JSON.stringify({ text, lang: "auto" }),
      });
      if (!resp.ok) {
        console.warn("playServerTTS failed", resp.status);
        return;
      }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      // Stop any existing audio
      try {
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
          audioRef.current = null;
        }
      } catch (e) {}

      const audio = new Audio(url);
      audioRef.current = audio;
      setIsSpeaking(true);
      audio.volume = Number(volume) || 1;
      audio.onplay = () => console.log("Server TTS playback started");
      audio.onended = () => {
        console.log("Server TTS playback ended");
        URL.revokeObjectURL(url);
        setIsSpeaking(false);
        audioRef.current = null;
      };
      audio.onerror = (e) => {
        console.warn("Server TTS playback error", e);
        setIsSpeaking(false);
        audioRef.current = null;
      };
      await audio.play();
    } catch (e) {
      console.warn("playServerTTS failed", e);
    }
  };

  // Debounced transliteration caller
  const scheduleTransliteration = useCallback((text: string) => {
    try {
      if (translitTimer.current) window.clearTimeout(translitTimer.current);
    } catch (e) {}
    translitTimer.current = window.setTimeout(async () => {
      setTransliterationLoading(true);
      try {
        const backendOrigin =
          (process.env.NEXT_PUBLIC_BACKEND_ORIGIN as string) ||
          "http://localhost:2355";
        const resp = await fetch(
          `${backendOrigin.replace(/\/$/, "")}/transliterate`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
          }
        );
        const j = await resp.json();
        if (j && j.transliteration) setTransliteration(j.transliteration);
      } catch (e) {
        console.warn("transliterate failed", e);
      } finally {
        setTransliterationLoading(false);
      }
    }, 300);
  }, []);
  // language/dialect is auto-detected by the server; no user selection
  // Read Aloud using server-side audio streaming (MediaSource)
  const readAloud = async () => {
    const text = textBoxContent.trim();
    if (!text) return;

    // If audio is already playing, stop it
    if (audioRef.current) {
      try {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      } catch (e) {}
      audioRef.current = null;
    }

    const backendOrigin =
      (process.env.NEXT_PUBLIC_BACKEND_ORIGIN as string) ||
      "http://localhost:2355";

    try {
      setIsSpeaking(true);
      setHighlightWordIndex(null);

      const resp = await fetch(`${backendOrigin.replace(/\/$/, "")}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "audio/mpeg" },
        body: JSON.stringify({ text, lang: "auto" }),
      });

      if (!resp.ok || !resp.body) {
        console.warn("Server TTS failed", resp.status);
        setIsSpeaking(false);
        return;
      }

      // Create audio element and MediaSource
      const mediaSource = new (window as any).MediaSource();
      mediaSourceRef.current = mediaSource;
      const audio = new Audio();
      audioRef.current = audio;
      audio.src = URL.createObjectURL(mediaSource);
      audio.volume = Number(volume) || 1;

      mediaSource.addEventListener("sourceopen", async () => {
        try {
          const mime = "audio/mpeg";
          const sourceBuffer: any = mediaSource.addSourceBuffer(mime);
          const body = resp.body;
          if (!body) {
            console.warn("response body is null");
            setIsSpeaking(false);
            return;
          }
          const reader = (body as ReadableStream<Uint8Array>).getReader();
          const queue: Uint8Array[] = [];
          let appending = false;

          const appendNext = () => {
            if (appending || !queue.length) return;
            appending = true;
            const chunk = queue.shift() as Uint8Array;
            try {
              sourceBuffer.appendBuffer(chunk);
            } catch (e) {
              console.warn("appendBuffer failed", e);
              appending = false;
            }
          };

          sourceBuffer.addEventListener("updateend", () => {
            appending = false;
            if (queue.length) appendNext();
          });

          // Read stream and enqueue
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            if (value) {
              queue.push(value);
              appendNext();
            }
          }

          // signal end of stream when buffer drained
          const waitForDrain = () => {
            if (!sourceBuffer.updating && queue.length === 0) {
              try {
                mediaSource.endOfStream();
              } catch (e) {}
              return;
            }
            setTimeout(waitForDrain, 50);
          };
          waitForDrain();
        } catch (e) {
          console.warn("mediaSource error", e);
        }
      });

      audio.onplaying = () => console.log("Server audio playing");
      audio.onended = () => {
        console.log("Server audio ended");
        setIsSpeaking(false);
        audioRef.current = null;
      };
      audio.onerror = (e) => {
        console.warn("Audio element error", e);
        setIsSpeaking(false);
      };

      // start playback once enough data is appended
      try {
        await audio.play();
      } catch (e) {
        // autoplay may be blocked until user gesture; user clicked Read Aloud so should be allowed
        console.warn("audio.play failed", e);
      }
    } catch (e) {
      console.warn("readAloud server stream failed", e);
      setIsSpeaking(false);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      try {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      } catch (e) {}
      audioRef.current = null;
    }
    if (mediaSourceRef.current) {
      try {
        mediaSourceRef.current = null;
      } catch (e) {}
    }
    setIsSpeaking(false);
  };

  // Populate voices list (browsers may load asynchronously)
  useEffect(() => {
    if (!(window as any).speechSynthesis) return;
    const load = () => {
      const v = (window as any).speechSynthesis.getVoices() || [];
      setVoices(v as SpeechSynthesisVoice[]);
      console.log(
        "SpeechSynthesis voices loaded:",
        v.map((x: any) => ({
          name: x.name,
          lang: x.lang,
          voiceURI: x.voiceURI,
        }))
      );
    };
    load();
    (window as any).speechSynthesis.onvoiceschanged = () => load();
  }, []);

  // Manual test helper: speak a short test phrase and log voices
  const testAudio = () => {
    if (!(window as any).speechSynthesis) {
      console.warn("speechSynthesis not available");
      return;
    }
    const v = (window as any).speechSynthesis.getVoices() || [];
    console.log(
      "Available voices (test):",
      v.map((x: any) => ({ name: x.name, lang: x.lang, voiceURI: x.voiceURI }))
    );
    const u = new SpeechSynthesisUtterance(
      "This is an audio test. If you hear this, audio is working."
    );
    u.onstart = () => console.log("Test utterance started");
    u.onend = () => console.log("Test utterance ended");
    try {
      (window as any).speechSynthesis.speak(u);
    } catch (e) {
      console.warn("Test speak failed", e);
    }
  };

  // Heuristic dialect detection from text (very small rule-based approach)
  const detectDialectFromText = (text: string) => {
    const t = text.toLowerCase();
    const scores: Record<string, number> = {
      "en-GB": 0,
      "en-AU": 0,
      "en-IN": 0,
      "en-CA": 0,
      "en-US": 0,
    };

    const addIfPresent = (words: string[], key: string) => {
      for (const w of words) if (t.includes(w)) scores[key]++;
    };

    // British spellings / words
    addIfPresent(
      ["colour", "favour", "centre", "theatre", "tyre", "realise", "organise"],
      "en-GB"
    );
    // Australian slang
    addIfPresent(["mate", "arvo", "servo", "cya", "barbie"], "en-AU");
    // Indian cues
    addIfPresent(
      ["ji", "yaar", "please", "sir", "madam", "bharat", "india"],
      "en-IN"
    );
    // Canadian cues
    addIfPresent(["eh?", "eh ", "colour", "centre", "honour"], "en-CA");
    // American spellings / words
    addIfPresent(
      [
        "color",
        "favor",
        "center",
        "theater",
        "truck",
        "honor",
        "organize",
        "realize",
      ],
      "en-US"
    );
    {
      /*
          <div className={styles.editPanel}>
            <input
              className={styles.editInput}
              placeholder="Type text here to read aloud..."
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              aria-label="Edit box to read"
            />
            <button
              type="button"
              className={styles.readBtn}
              onClick={() => speakText(editText)}
            >
              Read Edit
            </button>
          </div>
          */
    }
    // pick the highest scoring dialect from the heuristic
    let best = "en-US";
    let bestScore = -1;
    for (const k of Object.keys(scores)) {
      if (scores[k] > bestScore) {
        best = k;
        bestScore = scores[k];
      }
    }
    return best;
  };

  // Helper: pick a browser voice from a dialect string (e.g. 'en-GB')
  const pickVoiceForDialect = (dial: string, vlist: any[]) => {
    if (!vlist || vlist.length === 0) return null;
    // match lang startsWith dial (en-GB matches en-GB, en-GB-x), otherwise match language snippet
    const tryMatch = (prefix: string) =>
      vlist.find(
        (v: any) =>
          v.lang && v.lang.toLowerCase().startsWith(prefix.toLowerCase())
      );
    const byRegion = tryMatch(dial);
    if (byRegion) return byRegion;
    const en = vlist.find(
      (v: any) => v.lang && v.lang.toLowerCase().startsWith("en")
    );
    return en || vlist[0];
  };

  const sendTextAsQuery = (useHud = true) => {
    const text = textBoxContent.trim();
    if (!text) return;
    // put text into the query input and trigger search
    setQuery(text);
    if (useHud) {
      setConvoActive(true);
      setShowHud(true);
      setHudShrunk(false);
    }
    onSearch(text);
  };

  // Keyboard shortcut is handled on the textarea (Ctrl/Cmd+Enter)

  // Upload audio blob to backend /transcribe and feed transcript to onSearch
  const uploadAudioBlob = async (blob: Blob) => {
    setIsUploading(true);
    try {
      const backendOrigin =
        (process.env.NEXT_PUBLIC_BACKEND_ORIGIN as string) ||
        "http://localhost:2355";
      const fd = new FormData();
      fd.append("file", blob, "audio.webm");
      const resp = await fetch(
        `${backendOrigin.replace(/\/$/, "")}/transcribe`,
        {
          method: "POST",
          body: fd,
        }
      );
      const j = await resp.json();
      if (j && j.text) {
        setQuery(j.text);
        // trigger search with the transcript
        onSearch(j.text);
      }
    } catch (e) {
      console.warn("transcribe upload failed", e);
    } finally {
      setIsUploading(false);
    }
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn("getUserMedia not supported");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      recordedChunksRef.current = [];
      mr.ondataavailable = (ev: any) => {
        if (ev.data && ev.data.size > 0)
          recordedChunksRef.current.push(ev.data);
      };
      mr.onstop = () => {
        const blob = new Blob(recordedChunksRef.current, {
          type: "audio/webm",
        });
        // stop all tracks
        try {
          stream.getTracks().forEach((t) => t.stop());
        } catch (e) {}
        uploadAudioBlob(blob);
      };
      mediaRecorderRef.current = mr;
      mr.start();
      setIsRecording(true);
      // show HUD and shrink it when recording starts
      setShowHud(true);
      setHudShrunk(true);
    } catch (e) {
      console.warn("startRecording failed", e);
    }
  };

  const stopRecording = () => {
    try {
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        mediaRecorderRef.current.stop();
      }
    } catch (e) {}
    setIsRecording(false);
    // when recording stops, expand HUD to show assistant reply streaming
    setHudShrunk(false);
  };

  const onFileInput = async (f: File | null) => {
    if (!f) return;
    // convert to blob and upload
    await uploadAudioBlob(f);
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
      // cleanup SSE if left open
      try {
        if (eventSourceRef.current)
          (eventSourceRef.current as EventSource).close();
      } catch (e) {
        /* ignore */
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const toggleListen = () => {
    if (!recogRef.current) return;
    if (listening) {
      recogRef.current.stop();
      setListening(false);
      setHudShrunk(false);
    } else {
      recogRef.current.start();
      setListening(true);
      // open HUD and shrink
      setShowHud(true);
      setHudShrunk(true);
      // ensure input focused
      inputRef.current && inputRef.current.focus();
    }
  };

  const startConvo = () => {
    setConvoActive(true);
    // focus input so mic results are visible
    setTimeout(() => inputRef.current && inputRef.current.focus(), 50);
  };

  // Trigger a visual launch animation then start listening
  const startLaunch = () => {
    // start the launch animation on the button
    setLaunching(true);
  };

  const onLaunchAnimationEnd = () => {
    // finish morph: hide the launcher button and show HUD + listening
    setLaunching(false);
    setShowLauncher(false);
    startConvo();
    // start listening (toggleListen handles feature detection)
    try {
      if (recogRef.current && !listening) {
        recogRef.current.start();
        setListening(true);
        // show HUD and shrink it
        setShowHud(true);
        setHudShrunk(true);
        inputRef.current && inputRef.current.focus();
      } else if (!recogRef.current) {
        // fallback to recording flow if SpeechRecognition not available
        startRecording();
      }
    } catch (e) {
      // ignore
    }
  };

  // clicking the HUD circle toggles shrink state (simulate press/release)
  const onHudClick = () => {
    setHudShrunk((s) => !s);
  };

  return (
    <div className={styles.wrapper}>
      {onlyDemo ? (
        <div className={styles.onlyDemoWrap}>
          <input
            className={styles.editInput}
            placeholder="Type text here to read aloud..."
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            aria-label="Edit box to read"
          />
          <button
            type="button"
            className={styles.readBtn}
            onClick={() => speakText(editText)}
          >
            Read
          </button>
        </div>
      ) : (
        <>
          <div className={styles.controls}>
            {!convoActive ? (
              <div className={styles.startWrap}>
                <button
                  className={`${styles.stylishBtn} ${
                    launching ? styles.launching : ""
                  }`}
                  onClick={startLaunch}
                  onAnimationEnd={() => {
                    if (launching) onLaunchAnimationEnd();
                  }}
                  aria-label="Start conversation"
                  type="button"
                >
                  Start Conversation
                </button>
                <div className={styles.sub}>Focus on talking — press Start</div>
              </div>
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
            {convoActive && (
              <div style={{ marginTop: 8 }}>
                <button
                  type="button"
                  onClick={stopStream}
                  className={styles.stopBtn}
                >
                  Stop Stream
                </button>
                <div
                  style={{ marginTop: 6, fontSize: 12, color: "var(--muted)" }}
                >
                  Status: {connState}
                </div>
                <div style={{ marginTop: 6 }}>
                  <label
                    style={{
                      fontSize: 12,
                      color: "var(--muted)",
                      display: "flex",
                      gap: 8,
                      alignItems: "center",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={transliterateEnabled}
                      onChange={(e) =>
                        setTransliterateEnabled(e.target.checked)
                      }
                    />
                    <span>Transliterate</span>
                  </label>
                </div>
              </div>
            )}
            {convoActive && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  {!isRecording ? (
                    <button
                      className={styles.stylishBtn}
                      onClick={startRecording}
                      type="button"
                      disabled={isUploading}
                    >
                      Record
                    </button>
                  ) : (
                    <button
                      className={styles.stopBtn}
                      onClick={stopRecording}
                      type="button"
                    >
                      Stop Recording
                    </button>
                  )}

                  <label
                    className={styles.stylishBtn}
                    style={{ cursor: "pointer" }}
                  >
                    Upload File
                    <input
                      type="file"
                      accept="audio/*"
                      style={{ display: "none" }}
                      onChange={(e) =>
                        onFileInput(e.target.files ? e.target.files[0] : null)
                      }
                      disabled={isUploading}
                    />
                  </label>

                  {isUploading && (
                    <div style={{ fontSize: 12 }}>Uploading...</div>
                  )}
                </div>
              </div>
            )}
          </div>

          <SearchForm
            onSearch={onSearch}
            value={query}
            onChange={setQuery}
            inputRef={inputRef}
            compact={convoActive}
          />

          <div className={`${styles.editPanel} ${styles.hiddenDemo}`}>
            <input
              className={styles.editInput}
              placeholder="Type text here to read aloud..."
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              aria-label="Edit box to read"
            />
            <button
              type="button"
              className={styles.readBtn}
              onClick={() => speakText(editText)}
            >
              Read Edit
            </button>
          </div>
          {/* Small text box: user can type text that will only be read or sent as a query */}
          <div className={styles.textBoxWrap}>
            <textarea
              className={styles.textBox}
              placeholder="Type text here to read aloud or send as a query..."
              value={textBoxContent}
              onChange={(e) => {
                const v = e.target.value;
                setTextBoxContent(v);
                if (transliterateEnabled) scheduleTransliteration(v);
              }}
            />
            {/* transliteration controls */}
            <div
              style={{
                display: "flex",
                gap: 12,
                alignItems: "center",
                marginTop: 8,
              }}
            >
              <label
                style={{
                  fontSize: 12,
                  color: "var(--muted)",
                  display: "flex",
                  gap: 8,
                  alignItems: "center",
                }}
              >
                <input
                  type="checkbox"
                  checked={applyTransliteration}
                  onChange={(e) => setApplyTransliteration(e.target.checked)}
                />
                <span>Apply transliteration</span>
              </label>
              <label
                style={{
                  fontSize: 12,
                  color: "var(--muted)",
                  display: "flex",
                  gap: 8,
                  alignItems: "center",
                }}
              >
                <input
                  type="checkbox"
                  checked={autoApplyToQuery}
                  onChange={(e) => setAutoApplyToQuery(e.target.checked)}
                />
                <span>Auto-apply to query</span>
              </label>
              {transliteration && (
                <div
                  style={{ fontSize: 13, color: "var(--muted)" }}
                  aria-live="polite"
                >
                  {transliteration}
                  {transliterationLoading && (
                    <span
                      style={{
                        marginLeft: 8,
                        fontSize: 12,
                        color: "var(--muted)",
                      }}
                    >
                      Transliterating...
                    </span>
                  )}
                </div>
              )}
            </div>
            <div className={styles.textBoxActions}>
              {/* language is auto-detected by the server; no selector shown */}
              {/* Voice selection (populated from browser voices) */}
              <select
                className={styles.dialectSelect}
                value={selectedVoiceUri || ""}
                onChange={(e) => setSelectedVoiceUri(e.target.value || null)}
                aria-label="Voice"
              >
                <option value="">(auto voice)</option>
                {voices.map((v) => (
                  <option key={v.voiceURI} value={v.voiceURI}>
                    {v.name} — {v.lang}
                  </option>
                ))}
              </select>
              {/* If the user selects a browser voice, we can attempt to map its lang
            to an Azure voice name when calling the server /tts. */}
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <label style={{ color: "var(--muted)", fontSize: 12 }}>
                  Rate
                  <input
                    type="range"
                    min={0.5}
                    max={2}
                    step={0.1}
                    value={rate}
                    onChange={(e) => setRate(Number(e.target.value))}
                  />
                </label>
                <label style={{ color: "var(--muted)", fontSize: 12 }}>
                  Pitch
                  <input
                    type="range"
                    min={0.5}
                    max={2}
                    step={0.1}
                    value={pitch}
                    onChange={(e) => setPitch(Number(e.target.value))}
                  />
                </label>
                <label style={{ color: "var(--muted)", fontSize: 12 }}>
                  Volume
                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.1}
                    value={volume}
                    onChange={(e) => setVolume(Number(e.target.value))}
                  />
                </label>
              </div>
              <button
                type="button"
                className={styles.actionBtn}
                onClick={() => {
                  if (isSpeaking) stopAudio();
                  else readAloud();
                }}
                aria-pressed={isSpeaking}
              >
                {isSpeaking ? "Stop" : "Read Aloud"}
              </button>
              <button
                type="button"
                className={`${styles.actionBtn} ${styles.secondary}`}
                onClick={() => testAudio()}
                style={{ marginLeft: 8 }}
              >
                Test Audio
              </button>
              <button
                type="button"
                className={`${styles.actionBtn} ${styles.secondary}`}
                onClick={() => {
                  if (isSpeaking) stopAudio();
                  else playServerTTS();
                }}
                style={{ marginLeft: 8 }}
              >
                Play Server TTS
              </button>
              <button
                type="button"
                className={`${styles.actionBtn} ${styles.secondary}`}
                onClick={() => sendTextAsQuery(true)}
              >
                Send as Query
              </button>
              <div className={styles.speakingIndicator}>
                {isSpeaking ? "Speaking..." : ""}
              </div>
            </div>
          </div>
          {/* Render spoken text (e.g., Devanagari) with highlighting while speaking */}
          {spokenText && (
            <div className={styles.spokenLine} aria-live="polite">
              {spokenText.split(/\s+/).map((w, i) => (
                <span
                  key={i}
                  className={
                    i === highlightWordIndex ? styles.spokenWordHighlight : ""
                  }
                  style={{ marginRight: 6 }}
                >
                  {w}
                </span>
              ))}
            </div>
          )}

          {/* hide the page results while the HUD overlay is visible to avoid
              duplicated text bleeding through the semi-transparent backdrop */}
          {!showHud && (
            <div className={styles.results}>
              <ResultsList results={results} connState={connState} />
            </div>
          )}

          {/* HUD overlay for microphone conversation */}
          {showHud && (
            <div
              className={styles.hudOverlay}
              role="dialog"
              aria-hidden={!showHud}
            >
              <div
                className={styles.hudBackdrop}
                onClick={() => setShowHud(false)}
              />
              <div
                className={`${styles.hudCircle} ${
                  hudShrunk ? " " + styles.shrink : ""
                }`}
                onClick={onHudClick}
                role="button"
                aria-pressed={hudShrunk}
                tabIndex={0}
              >
                <div className={styles.hudText}>
                  {/* Stream display: single scrollable area with live text + typing cursor */}
                  <div className={styles.hudStream} aria-live="polite">
                    <div className={styles.streamText}>
                      {liveTranscript ||
                        (isRecording || listening
                          ? "Speak now"
                          : "No response yet")}
                    </div>
                    {/* Typing cursor shown only when connection is open or recording/listening */}
                    {(connState === "open" || isRecording || listening) && (
                      <span
                        className={styles.typingCursor}
                        aria-hidden="true"
                      />
                    )}
                  </div>
                  {/* Transliteration line (if enabled) */}
                  {transliterateEnabled && (
                    <div className={styles.translitLine} aria-live="polite">
                      {transliteration || "..."}
                    </div>
                  )}
                </div>
                <div className={styles.hudSub}>Click circle to toggle</div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
