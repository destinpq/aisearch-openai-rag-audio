import { DocumentsService } from "./documents.service";

export async function runIngest(documentId: string, filepath: string) {
  const svc = new DocumentsService();
  return svc.ingestDocument(documentId, filepath);
}
