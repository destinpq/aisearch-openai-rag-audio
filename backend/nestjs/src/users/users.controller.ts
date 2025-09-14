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
import { UsersService } from "./users.service";
import { CreateUserDto } from "./dto/create-user.dto";
import { UpdateUserDto } from "./dto/update-user.dto";

@Controller("users")
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  getAll() {
    return this.usersService.findAll();
  }

  @Get(":id")
  getOne(@Param("id") id: string) {
    const user = this.usersService.findById(id);
    if (!user) throw new NotFoundException("User not found");
    return user;
  }

  @Post()
  create(@Body() body: CreateUserDto) {
    return this.usersService.create(body as any);
  }

  @Put(":id")
  update(@Param("id") id: string, @Body() body: UpdateUserDto) {
    const u = this.usersService.update(id, body as any);
    if (!u) throw new NotFoundException("User not found");
    return u;
  }

  @Delete(":id")
  remove(@Param("id") id: string) {
    const ok = this.usersService.delete(id);
    if (!ok) throw new NotFoundException("User not found");
    return { deleted: ok };
  }
}
