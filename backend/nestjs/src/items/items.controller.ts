import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  NotFoundException,
} from "@nestjs/common";
import { ItemsService } from "./items.service";
import { CreateItemDto } from "./dto/create-item.dto";
import { UpdateItemDto } from "./dto/update-item.dto";

@Controller("items")
export class ItemsController {
  constructor(private readonly itemsService: ItemsService) {}

  @Get()
  getAll() {
    return this.itemsService.findAll();
  }

  @Get(":id")
  getOne(@Param("id") id: string) {
    const it = this.itemsService.findById(id);
    if (!it) throw new NotFoundException("Item not found");
    return it;
  }

  @Post()
  create(@Body() body: CreateItemDto) {
    return this.itemsService.create(body as any);
  }

  @Put(":id")
  update(@Param("id") id: string, @Body() body: UpdateItemDto) {
    const u = this.itemsService.update(id, body as any);
    if (!u) throw new NotFoundException("Item not found");
    return u;
  }

  @Delete(":id")
  remove(@Param("id") id: string) {
    const ok = this.itemsService.delete(id);
    if (!ok) throw new NotFoundException("Item not found");
    return { deleted: ok };
  }
}
