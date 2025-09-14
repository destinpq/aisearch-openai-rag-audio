import fetch from "node-fetch";

const AZURE_ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT || "";
const AZURE_KEY = process.env.AZURE_OPENAI_KEY || "";
const AZURE_DEPLOYMENT = process.env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT || "";
const AZURE_API_VERSION = process.env.AZURE_OPENAI_API_VERSION || "2024-10-01";

if (!AZURE_ENDPOINT || !AZURE_KEY || !AZURE_DEPLOYMENT) {
  console.warn("Azure OpenAI embedding env vars not fully configured");
}

export async function embedTexts(texts: string[]): Promise<number[][]> {
  if (!AZURE_ENDPOINT || !AZURE_KEY || !AZURE_DEPLOYMENT) {
    throw new Error("Azure embedding configuration missing");
  }

  const url = `${AZURE_ENDPOINT}/openai/deployments/${AZURE_DEPLOYMENT}/embeddings?api-version=${AZURE_API_VERSION}`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "api-key": AZURE_KEY },
    body: JSON.stringify({ input: texts }),
  });

  if (!resp.ok) {
    const txt = await resp.text();
    throw new Error(`Azure embeddings error: ${resp.status} ${txt}`);
  }

  const json = await resp.json();
  // response.data -> [{embedding: [...]}, ...]
  return json.data.map((d: any) => d.embedding as number[]);
}
