"use client";
import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

export default function useRealtime() {
  const socketRef = useRef<Socket | null>(null);
  const [messages, setMessages] = useState<any[]>([]);

  useEffect(() => {
    const s = io(undefined, { path: "/realtime" });
    socketRef.current = s;
    s.on("connect", () => console.log("realtime connected"));
    s.on("response.chunk", (chunk: any) =>
      setMessages((prev) => [...prev, chunk])
    );
    s.on("response.done", () => console.log("done"));
    return () => {
      s.disconnect();
    };
  }, []);

  return { socket: socketRef.current, messages };
}
