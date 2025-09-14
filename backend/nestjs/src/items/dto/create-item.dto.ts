import { IsNotEmpty, IsOptional, IsString } from "class-validator";

export class CreateItemDto {
  @IsNotEmpty()
  @IsString()
  name: string;

  @IsOptional()
  @IsString()
  description?: string;
}
