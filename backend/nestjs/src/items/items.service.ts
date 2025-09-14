import { Injectable } from "@nestjs/common";
import { Item } from "./item.model";
import { getDb } from "../db/sqlite.helper";
import { randomUUID } from "crypto";

@Injectable()
export class ItemsService {
  private db = getDb();

  findAll(): Item[] {
    const stmt = this.db.prepare("SELECT id,name,description FROM items");
    return stmt.all() as Item[];
  }

  findById(id: string): Item | undefined {
    const stmt = this.db.prepare(
      "SELECT id,name,description FROM items WHERE id = ?"
    );
    return stmt.get(id) as Item | undefined;
  }

  create(payload: { name: string; description?: string }): Item {
    const id = randomUUID();
    const stmt = this.db.prepare(
      "INSERT INTO items (id,name,description) VALUES (?,?,?)"
    );
    stmt.run(id, payload.name, payload.description || null);
    return { id, ...payload };
  }

  update(
    id: string,
    payload: { name?: string; description?: string }
  ): Item | undefined {
    const existing = this.findById(id);
    if (!existing) return undefined;
    const name = payload.name ?? existing.name;
    const description = payload.description ?? existing.description;
    const stmt = this.db.prepare(
      "UPDATE items SET name = ?, description = ? WHERE id = ?"
    );
    stmt.run(name, description, id);
    return { id, name, description };
  }

  delete(id: string): boolean {
    const stmt = this.db.prepare("DELETE FROM items WHERE id = ?");
    const info = stmt.run(id);
    return info.changes > 0;
  }
}
