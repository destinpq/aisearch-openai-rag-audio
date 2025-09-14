import { Injectable, Logger } from "@nestjs/common";
import { getPg } from "../db/postgres.helper";
import { embedTexts } from "../azure/azure.embeddings";

type SessionState = { language?: string; interrupted?: boolean };

@Injectable()
export class RealtimeService {
  private readonly logger = new Logger(RealtimeService.name);
  private sessions = new Map<string, SessionState>();

  setLanguage(sessionId: string, language: string) {
    const s = this.sessions.get(sessionId) || {};
    s.language = language;
    this.sessions.set(sessionId, s);
    this.logger.log(`Session ${sessionId} language set to ${language}`);
  }

  startProcessing(sessionId: string) {
    const s = this.sessions.get(sessionId) || {};
    s.interrupted = false;
    this.sessions.set(sessionId, s);
  }

  interrupt(sessionId: string) {
    const s = this.sessions.get(sessionId) || {};
    s.interrupted = true;
    this.sessions.set(sessionId, s);
    this.logger.log(`Session ${sessionId} interrupted`);
  }

  isInterrupted(sessionId: string) {
    const s = this.sessions.get(sessionId) || {};
    return !!s.interrupted;
  }

  // Retrieve nearest chunks for `query` and return them as an array of metadata objects.
  // Returns { interrupted: boolean, chunks: Array<{text, documentId, page, lineNo, startChar, endChar, distance}> }
  async retrieveAndAnswer(query: string, sessionId: string) {
    if (this.isInterrupted(sessionId)) return { interrupted: true, chunks: [] };

    const embeddings = await embedTexts([query]);
    const qEmb = embeddings[0];

    const pool = await getPg();
    const client = await pool.connect();
    try {
      const res = await client.query(
        `SELECT id, document_id, chunk_text, token_text, page, line_no, start_char, end_char,
                embedding <-> $1::vector AS distance
         FROM document_tokens
         ORDER BY embedding <-> $1::vector
         LIMIT 10`,
        [qEmb]
      );

      const rows = res.rows || [];
      const chunks: Array<any> = [];
      for (const r of rows) {
        if (this.isInterrupted(sessionId))
          return { interrupted: true, chunks: [] };
        chunks.push({
          text: r.chunk_text || r.token_text || "",
          documentId: r.document_id,
          page: r.page,
          lineNo: r.line_no,
          startChar: r.start_char,
          endChar: r.end_char,
          distance: r.distance,
        });
      }
      return { interrupted: false, chunks };
    } finally {
      client.release();
    }
  }
}
