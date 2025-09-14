import { RealtimeGateway } from "../src/realtime/realtime.gateway";
import { RealtimeService } from "../src/realtime/realtime.service";

// Minimal fake socket to capture emitted events
class FakeClient {
  id = "test-client";
  emitted: any[] = [];
  emit(event: string, payload: any) {
    this.emitted.push({ event, payload });
  }
}

describe("RealtimeGateway streaming", () => {
  it("emits chunk metadata and done", async () => {
    const fakeService = new RealtimeService();
    // stub retrieveAndAnswer
    // @ts-ignore
    fakeService.retrieveAndAnswer = async (q: string, s: string) => {
      return {
        interrupted: false,
        chunks: [
          { text: "chunk1", documentId: 1, page: 1, lineNo: 1 },
          { text: "chunk2", documentId: 1, page: 2, lineNo: 5 },
        ],
      };
    };

    const gateway = new RealtimeGateway(fakeService as any);
    const client = new FakeClient();

    await gateway.handleQuery(client as any, { text: "hello" });

    // expect two response.chunk and one response.done
    const chunkEvents = client.emitted.filter(
      (e) => e.event === "response.chunk"
    );
    const doneEvents = client.emitted.filter(
      (e) => e.event === "response.done"
    );

    if (chunkEvents.length !== 2) throw new Error("expected 2 chunk events");
    if (doneEvents.length !== 1) throw new Error("expected 1 done event");
  });
});
