import { Injectable } from "@nestjs/common";
import { User } from "./user.model";
import { randomUUID } from "crypto";
import { getDb } from "../db/sqlite.helper";

@Injectable()
export class UsersService {
  private db = getDb();

  findAll(): User[] {
    const stmt = this.db.prepare("SELECT id,name,email FROM users");
    return stmt.all() as User[];
  }

  findById(id: string): User | undefined {
    const stmt = this.db.prepare(
      "SELECT id,name,email FROM users WHERE id = ?"
    );
    return stmt.get(id) as User | undefined;
  }

  create(payload: { name: string; email?: string }): User {
    const id = randomUUID();
    const stmt = this.db.prepare(
      "INSERT INTO users (id,name,email) VALUES (?,?,?)"
    );
    stmt.run(id, payload.name, payload.email || null);
    return { id, ...payload } as User;
  }

  update(
    id: string,
    payload: { name?: string; email?: string }
  ): User | undefined {
    const existing = this.findById(id);
    if (!existing) return undefined;
    const name = payload.name ?? existing.name;
    const email = payload.email ?? existing.email;
    const stmt = this.db.prepare(
      "UPDATE users SET name = ?, email = ? WHERE id = ?"
    );
    stmt.run(name, email, id);
    return { id, name, email } as User;
  }

  delete(id: string): boolean {
    const stmt = this.db.prepare("DELETE FROM users WHERE id = ?");
    const info = stmt.run(id);
    return info.changes > 0;
  }
}
