import { join, dirname, sep } from "path";
import * as fs from "fs";
// better-sqlite3 is a CommonJS module; require it to avoid the default-import mismatch.
const Database = require("better-sqlite3");

// Choose DB path that works both when running from source (src) and from compiled dist
// If runtime __dirname contains '/dist/' use ../../../data, otherwise use ../../data
const DB_PATH = __dirname.includes(`${sep}dist${sep}`)
  ? join(__dirname, "../../../data/nestjs.db")
  : join(__dirname, "../../data/nestjs.db");

export function getDb() {
  const dbDir = dirname(DB_PATH);
  try {
    // ensure parent directory exists (idempotent)
    fs.mkdirSync(dbDir, { recursive: true });
  } catch (err) {
    console.error("Failed to create sqlite data directory", dbDir, err);
  }

  console.debug("Opening SQLite DB at", DB_PATH);

  let db;
  try {
    db = new Database(DB_PATH);
  } catch (err) {
    console.error("Failed to open SQLite DB at", DB_PATH, err);
    throw err;
  }

  db.exec(
    `CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, name TEXT, description TEXT);
     CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, email TEXT)`
  );
  return db;
}
