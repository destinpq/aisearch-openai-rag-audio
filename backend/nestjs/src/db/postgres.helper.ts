import { Pool } from "pg";
import { join } from "path";

const DATABASE_URL =
  process.env.DATABASE_URL || process.env.PG_CONNECTION_STRING || "";

let pool: Pool | null = null;

if (!DATABASE_URL) {
  console.warn(
    "Warning: DATABASE_URL not set; Postgres integration will be disabled. To enable, set DATABASE_URL to your Postgres connection string."
  );
} else {
  pool = new Pool({ connectionString: DATABASE_URL });
}

export async function getPg() {
  if (!pool) {
    throw new Error(
      "DATABASE_URL not configured - Postgres pool is unavailable"
    );
  }
  return pool;
}

export async function ensureSchema(embeddingDim = 1536) {
  if (!pool) {
    // Skip schema creation when no Postgres is configured
    console.warn("Skipping ensureSchema: DATABASE_URL not configured");
    return;
  }

  const client = await pool.connect();
  try {
    // Extension and tables
    await client.query(`CREATE EXTENSION IF NOT EXISTS vector;`);

    await client.query(`
      CREATE TABLE IF NOT EXISTS documents (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        filename text NOT NULL,
        uploaded_at timestamptz DEFAULT now(),
        filesize bigint,
        mime text,
        metadata jsonb
      );
    `);

    await client.query(`
      CREATE TABLE IF NOT EXISTS document_tokens (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page int NOT NULL,
        line_no int NOT NULL,
        start_char int NOT NULL,
        end_char int NOT NULL,
        token_text text NOT NULL,
        chunk_text text NOT NULL,
        token_index int NOT NULL,
        embedding vector(${embeddingDim}),
        created_at timestamptz DEFAULT now(),
        extra jsonb
      );
    `);

    // Index (user must tune for production)
    await client.query(`
      DO $$
      BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'document_tokens_embedding_idx') THEN
          CREATE INDEX document_tokens_embedding_idx ON document_tokens USING ivfflat (embedding) WITH (lists = 100);
        END IF;
      END$$;
    `);
  } finally {
    client.release();
  }
}
