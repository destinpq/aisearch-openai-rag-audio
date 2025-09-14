import { Module } from "@nestjs/common";
import { UsersModule } from "./users/users.module";
import { RealtimeModule } from "./realtime/realtime.module";
import { DocumentsModule } from "./documents/documents.module";
import { ItemsController } from "./items/items.controller";
import { ItemsService } from "./items/items.service";
import { HealthController } from "./health/health.controller";

@Module({
  imports: [UsersModule, RealtimeModule, DocumentsModule],
  controllers: [ItemsController, HealthController],
  providers: [ItemsService],
})
export class AppModule {}
