import { expect } from "chai";
import { ItemsService } from "../src/items/items.service";

describe("ItemsService (smoke)", () => {
  it("creates and finds an item", () => {
    const svc = new ItemsService();
    const created = svc.create({ name: "t", description: "d" });
    const found = svc.findById(created.id);
    expect(found).to.be.an("object");
    expect(found!.name).to.equal("t");
  });
});
