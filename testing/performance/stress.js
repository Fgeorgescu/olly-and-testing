/**
 * Stress test — pushes beyond normal load to find the breaking point.
 * Ramps aggressively to 100 VUs, then spikes to 150, then recovers.
 */
import { sleep } from "k6";
import {
  searchItems, createItem, deleteItem, placeHold, releaseHold,
  expectStatus,
} from "./lib/helpers.js";

export const options = {
  stages: [
    { duration: "1m",  target: 50  },  // ramp to normal-ish
    { duration: "2m",  target: 50  },  // sustain
    { duration: "1m",  target: 100 },  // push harder
    { duration: "2m",  target: 100 },  // sustain stress level
    { duration: "1m",  target: 150 },  // spike
    { duration: "1m",  target: 150 },  // hold the spike
    { duration: "2m",  target: 0   },  // recovery
  ],
  thresholds: {
    // Looser than load — we expect degradation, we want to see where it breaks
    http_req_failed: ["rate<0.10"],        // alert if >10% errors
    http_req_duration: ["p(95)<3000"],     // alert if p95 > 3s
  },
};

export default function () {
  const roll = Math.random();

  if (roll < 0.70) {
    // Heavy read bias under stress
    const list = searchItems();
    expectStatus(list, 200, "list items");
    sleep(0.5);

  } else if (roll < 0.90) {
    const create = createItem();
    expectStatus(create, 201, "create item");

    // Always clean up under stress to avoid DB pressure from accumulation
    if (create.status === 201) {
      deleteItem(create.json().id);
    }
    sleep(0.5);

  } else {
    // Hold + release (no confirm — keeps items reusable)
    const create = createItem();
    if (create.status !== 201) { sleep(1); return; }
    const itemId = create.json().id;

    const hold = placeHold(itemId);
    expectStatus(hold, 201, "place hold");

    if (hold.status === 201) {
      releaseHold(itemId);
    }

    deleteItem(itemId);
    sleep(0.5);
  }
}
