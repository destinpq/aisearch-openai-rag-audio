export type LocationInfo = {
    start_line?: number;
    end_line?: number;
    pages?: number[];
    line_numbers?: number[];
};

export type GroundingFile = {
    id: string;
    name: string;
    content: string;
    location?: LocationInfo;
};

export type HistoryItem = {
    id: string;
    transcript: string;
    groundingFiles: GroundingFile[];
};

export type IndexedDocument = {
    id: string;
    fact: string;
    title: string;
    created_at: string;
};

export type Conversation = {
    id: string;
    user_id: string;
    title?: string;
    status: string;
    created_at: string;
    updated_at: string;
    total_messages: number;
    duration_seconds: number;
    metadata?: Record<string, any>;
};

export type Message = {
    id: string;
    conversation_id: string;
    user_id: string;
    content: string;
    message_type: string;
    timestamp: string;
    metadata?: Record<string, any>;
};

export type SessionUpdateCommand = {
    type: "session.update";
    session: {
        turn_detection?: {
            type: "server_vad" | "none";
        };
        input_audio_transcription?: {
            model: "whisper-1";
        };
    };
};

export type InputAudioBufferAppendCommand = {
    type: "input_audio_buffer.append";
    audio: string;
};

export type InputAudioBufferClearCommand = {
    type: "input_audio_buffer.clear";
};

export type RealtimeMessage = {
    type: string;
};

export type ResponseAudioDelta = {
    type: "response.audio.delta";
    delta: string;
};

export type ResponseAudioTranscriptDelta = {
    type: "response.audio_transcript.delta";
    delta: string;
};

export type ResponseInputAudioTranscriptionCompleted = {
    type: "conversation.item.input_audio_transcription.completed";
    event_id: string;
    item_id: string;
    content_index: number;
    transcript: string;
};

export type ResponseDone = {
    type: "response.done";
    event_id: string;
    response: {
        id: string;
        output: { id: string; content?: { transcript: string; type: string }[] }[];
    };
};

export type ExtensionMiddleTierToolResponse = {
    type: "extension.middle_tier_tool.response";
    previous_item_id: string;
    tool_name: string;
    tool_result: string; // JSON string that needs to be parsed into ToolResult
};

export type ToolResult = {
    sources: {
        chunk_id: string;
        title: string;
        chunk: string;
        location?: LocationInfo;
    }[];
};
