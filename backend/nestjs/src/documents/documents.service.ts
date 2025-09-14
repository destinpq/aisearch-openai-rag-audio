import { Injectable, Logger } from "@nestjs/common";
import { getPg, ensureSchema } from "../db/postgres.helper";
import { embedTexts } from "../azure/azure.embeddings";
import { randomUUID } from "crypto";
import * as fs from "fs";
import { join } from "path";
import pdf from "pdf-parse";

@Injectable()
export class DocumentsService {
  private readonly logger = new Logger(DocumentsService.name);

  constructor() {
    // ensure schema exists (best to run migrations elsewhere)
    ensureSchema().catch((err) =>
      this.logger.error("ensureSchema failed", err)
    );
  }

  async saveFile(fileBuffer: Buffer, filename: string, mime: string) {
    const dir = join(process.cwd(), "data", "uploads");
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const id = randomUUID();
    const filepath = join(dir, `${id}-${filename}`);
    fs.writeFileSync(filepath, fileBuffer);
    // insert document row and return id
    const pool = await getPg();
    const res = await pool.query(
      "INSERT INTO documents(filename, filesize, mime) VALUES($1,$2,$3) RETURNING id",
      [filename, fileBuffer.length, mime]
    );
    const documentId = res.rows[0].id;
    return { documentId, filepath };
  }

  // Use pdf-parse to extract text split by pages and lines
  async extractPagesLines(filepath: string) {
    const dataBuffer = fs.readFileSync(filepath);
    const data = await pdf(dataBuffer, { max: 0 });
    const pages = data.text.split("\f");
    return pages.map((p) => p.split(/\r?\n/));
  }

  tokenizePageLines(pagesLines: string[][]) {
    const tokens: any[] = [];
    let index = 0;
    for (let pageIdx = 0; pageIdx < pagesLines.length; pageIdx++) {
      const lines = pagesLines[pageIdx];
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        let cursor = 0;
        const words = line.split(/\s+/).filter(Boolean);
        for (const w of words) {
          const start = line.indexOf(w, cursor);
          const end = start + w.length;
          tokens.push({
            page: pageIdx + 1,
            line_no: i + 1,
            start_char: start,
            end_char: end,
            token_text: w,
            chunk_text: w,
            token_index: index++,
          });
          cursor = end;
        }
      }
    }
    return tokens;
  }

  async ingestDocument(documentId: string, filepath: string) {
    const pagesLines = await this.extractPagesLines(filepath);
    const tokens = this.tokenizePageLines(pagesLines);
    // batch embeddings by chunk_text
    const chunks = tokens.map((t) => t.chunk_text);
    const embeddings = await embedTexts(chunks);
    const pool = await getPg();
    const client = await pool.connect();
    try {
      await client.query("BEGIN");
      const insertSql = `INSERT INTO document_tokens (document_id,page,line_no,start_char,end_char,token_text,chunk_text,token_index,embedding)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)`;
      for (let i = 0; i < tokens.length; i++) {
        const t = tokens[i];
        const emb = embeddings[i];
        await client.query(insertSql, [
          documentId,
          t.page,
          t.line_no,
          t.start_char,
          t.end_char,
          t.token_text,
          t.chunk_text,
          t.token_index,
          emb,
        ]);
      }
      await client.query("COMMIT");
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
    return { tokensCount: tokens.length };
  }
}
