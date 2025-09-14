// @ts-nocheck
import {
  SubscribeMessage,
  WebSocketGateway,
  OnGatewayInit,
  WebSocketServer,
} from "@nestjs/websockets";
import { Logger } from "@nestjs/common";
// Avoid direct socket.io type dependency in this environment; use flexible any types.
type Server = any;
type Socket = any;
import { RealtimeService } from "./realtime.service";

@WebSocketGateway({ namespace: "/realtime", cors: true })
export class RealtimeGateway implements OnGatewayInit {
  @WebSocketServer()
  server: Server;

  private readonly logger = new Logger(RealtimeGateway.name);

  constructor(private readonly realtime: RealtimeService) {}

  afterInit() {
    this.logger.log("Realtime gateway initialized");
  }

  handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage("session.update")
  handleSessionUpdate(client: Socket, payload: any) {
    const sessionId = client.id;
    if (payload?.session?.language) {
      this.realtime.setLanguage(sessionId, payload.session.language);
    }
    // acknowledge
    client.emit("session.updated", { ok: true });
  }

  @SubscribeMessage("session.interrupt")
  handleSessionInterrupt(client: Socket) {
    const sessionId = client.id;
    this.realtime.interrupt(sessionId);
    client.emit("session.interrupted", { ok: true });
  }

  @SubscribeMessage("query.ask")
  async handleQuery(client: Socket, payload: { text: string }) {
    const sessionId = client.id;
    this.realtime.startProcessing(sessionId);
    // retrieval returns { interrupted: boolean, chunks: string[] }
    const res = await this.realtime.retrieveAndAnswer(payload.text, sessionId);
    if (res.interrupted) {
      client.emit("response.interrupted", { reason: "interrupted" });
      return;
    }
    for (const c of res.chunks || []) {
      if (this.realtime.isInterrupted(sessionId)) {
        client.emit("response.interrupted", { reason: "interrupted" });
        return;
      }
      // emit chunk metadata as-is
      client.emit("response.chunk", { chunk: c });
      // slight pause to allow client-side processing (non-blocking)
      await new Promise((r) => setTimeout(r, 5));
    }
    client.emit("response.done", { done: true });
  }
}
