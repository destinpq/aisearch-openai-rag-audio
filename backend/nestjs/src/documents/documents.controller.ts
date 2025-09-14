/// <reference types="express" />
// ensure Express types are available for multer types
import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  Body,
  Get,
  Param,
  Res,
} from "@nestjs/common";
import { FileInterceptor } from "@nestjs/platform-express";
import { DocumentsService } from "./documents.service";
import { Response } from "express";

@Controller("process-pdf")
export class DocumentsController {
  constructor(private readonly docs: DocumentsService) {}

  @Post("test")
  test() {
    return { ok: true };
  }

  @Post()
  @UseInterceptors(FileInterceptor("file"))
  async upload(@UploadedFile() file: any) {
    const { documentId, filepath } = await this.docs.saveFile(
      file.buffer,
      file.originalname,
      file.mimetype
    );
    // kick off ingestion synchronously for now (could be background job)
    this.docs.ingestDocument(documentId, filepath).catch((err) => {
      console.error("Ingest failed", err);
    });
    return { document_id: documentId, message: "uploaded" };
  }

  @Get(":id")
  async status(@Param("id") id: string, @Res() res: Response) {
    // placeholder status response; production should read job state
    return res.json({
      status: "processing",
      total_chunks: 0,
      processed_chunks: 0,
      indexed_chunks: 0,
    });
  }
}
