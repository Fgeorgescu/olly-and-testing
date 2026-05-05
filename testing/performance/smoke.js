/**
 * Smoke test — 1 VU, 1 minute.
 * Verifies every endpoint responds correctly under negligible load.
 */
import { sleep } from "k6";
import {
  searchItems, getItem, createItem, deleteItem,
  placeHold, releaseHold, expectStatus,
} from "./lib/helpers.js";

export const options = {
  vus: 1,
  duration: "1m",
  thresholds: {
    http_req_failed: ["rate<0.01"],           // <1% errors
    http_req_duration: ["p(95)<500"],         // p95 under 500ms
  },
};

export default function () {
  // Browse
  const list = searchItems();
  expectStatus(list, 200, "list items");

  // Create
  const create = createItem();
  expectStatus(create, 201, "create item");
  const item = create.json();

  // Read
  const read = getItem(item.id);
  expectStatus(read, 200, "get item");

  // Hold flow
  const hold = placeHold(item.id);
  expectStatus(hold, 201, "place hold");

  const release = releaseHold(item.id);
  expectStatus(release, 200, "release hold");

  // Cleanup
  const del = deleteItem(item.id);
  expectStatus(del, 204, "delete item");

  sleep(1);
}
