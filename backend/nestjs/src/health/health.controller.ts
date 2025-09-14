import { Controller, Get } from "@nestjs/common";

// Use empty controller path and explicit GET('api') so with any global prefix
// the route resolves exactly to GET /api
@Controller()
export class HealthController {
  @Get()
  health() {
    return { ok: true, message: "converse-api running" };
  }
}
