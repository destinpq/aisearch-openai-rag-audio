const request = require("supertest");
import { expect } from "chai";

describe("Integration API (requires server on 3002)", () => {
  const base = "http://localhost:3002";

  it("creates and lists an item", async () => {
    const res = await request(base).post("/api/items").send({ name: "it1" });
    expect(res.status).to.equal(201);
    expect(res.body).to.have.property("id");

    const list = await request(base).get("/api/items");
    expect(list.status).to.equal(200);
    expect(list.body).to.be.an("array");
  });

  it("creates and lists a user", async () => {
    const r = await request(base).post("/api/users").send({ name: "intuser" });
    expect(r.status).to.equal(201);
    const u = await request(base).get("/api/users");
    expect(u.status).to.equal(200);
    expect(u.body.some((x: any) => x.name === "intuser")).to.be.true;
  });
});
