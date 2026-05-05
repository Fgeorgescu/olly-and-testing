/**
 * Load test — simulates normal expected traffic.
 * Ramps to 20 VUs, sustains for 3 minutes, then ramps down.
 *
 * Traffic mix (realistic marketplace):
 *   60% browsing (search + item detail)
 *   30% listing creation
 *   10% purchase hold flow
 */
import { sleep } from "k6";
import {
  searchItems, getItem, createItem, deleteItem,
  placeHold, releaseHold, confirmHold,
  expectStatus, SELLER_ID, BUYER_ID,
} from "./lib/helpers.js";

export const options = {
  stages: [
    { duration: "1m", target: 20 },   // ramp up
    { duration: "3m", target: 20 },   // sustain
    { duration: "30s", target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.02"],         // <2% errors
    http_req_duration: ["p(95)<1000"],      // p95 under 1s
    "http_req_duration{name:GET /items}": ["p(95)<500"],
    "http_req_duration{name:POST /items}": ["p(95)<800"],
  },
};

export default function () {
  const roll = Math.random();

  if (roll < 0.60) {
    // Browse
    const list = searchItems();
    expectStatus(list, 200, "list items");

    const items = list.json("items");
    if (items && items.length > 0) {
      const detail = getItem(items[0].id);
      expectStatus(detail, 200, "get item");
    }
    sleep(1);

  } else if (roll < 0.90) {
    // Create and optionally delete
    const create = createItem();
    expectStatus(create, 201, "create item");
    sleep(0.5);

    // 50% chance of cleanup so we don't accumulate infinite items
    if (Math.random() < 0.5) {
      deleteItem(create.json().id);
    }
    sleep(0.5);

  } else {
    // Full hold flow: create → hold → both confirm → sold
    const create = createItem();
    expectStatus(create, 201, "create item");
    const itemId = create.json().id;

    const hold = placeHold(itemId);
    expectStatus(hold, 201, "place hold");

    confirmHold(itemId, BUYER_ID);
    confirmHold(itemId, SELLER_ID);

    sleep(1);
  }
}
