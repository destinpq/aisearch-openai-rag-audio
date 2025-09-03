import { useRef } from "react";
import { Recorder } from "@/components/audio/recorder";

const BUFFER_SIZE = 4800;

type Parameters = {
    onAudioRecorded: (base64: string) => void;
};

export default function useAudioRecorder({ onAudioRecorded }: Parameters) {
    const audioRecorder = useRef<Recorder>();

    let buffer = new Uint8Array();

    const appendToBuffer = (newData: Uint8Array) => {
        const newBuffer = new Uint8Array(buffer.length + newData.length);
        newBuffer.set(buffer);
        newBuffer.set(newData, buffer.length);
        buffer = newBuffer;
    };

    const handleAudioData = (data: Iterable<number>) => {
        const uint8Array = new Uint8Array(data);
        appendToBuffer(uint8Array);

        if (buffer.length >= BUFFER_SIZE) {
            const toSend = new Uint8Array(buffer.slice(0, BUFFER_SIZE));
            buffer = new Uint8Array(buffer.slice(BUFFER_SIZE));

            const regularArray = String.fromCharCode(...toSend);
            const base64 = btoa(regularArray);

            onAudioRecorded(base64);
        }
    };

    const start = async () => {
        try {
            if (!audioRecorder.current) {
                audioRecorder.current = new Recorder(handleAudioData);
            }

            // Check if microphone permission is available
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error("Microphone access is not supported in this browser");
            }

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioRecorder.current.start(stream);
        } catch (error) {
            console.error("Failed to access microphone:", error);
            if (error instanceof DOMException) {
                if (error.name === "NotAllowedError") {
                    throw new Error("Microphone permission denied. Please allow microphone access and try again.");
                } else if (error.name === "NotFoundError") {
                    throw new Error("No microphone found. Please connect a microphone and try again.");
                } else if (error.name === "NotReadableError") {
                    throw new Error("Microphone is already in use by another application.");
                }
            }
            throw error;
        }
    };

    const stop = async () => {
        await audioRecorder.current?.stop();
    };

    return { start, stop };
}
