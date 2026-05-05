import http from "k6/http";
import { check } from "k6";

export const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

// Stub IDs — matches the server-side anonymous auth dependency
export const SELLER_ID = "00000000-0000-0000-0000-000000000001";
export const BUYER_ID = "00000000-0000-0000-0000-000000000002";

const JSON_HEADERS = { "Content-Type": "application/json" };

export function searchItems(params = {}) {
  const parts = [];
  if (params.q) parts.push(`q=${encodeURIComponent(params.q)}`);
  if (params.category) parts.push(`category=${encodeURIComponent(params.category)}`);
  const qs = parts.length ? `?${parts.join("&")}` : "";
  return http.get(`${BASE_URL}/api/v1/items${qs}`, { tags: { name: "GET /items" } });
}

export function getItem(id) {
  return http.get(`${BASE_URL}/api/v1/items/${id}`, {
    tags: { name: "GET /items/:id" },
  });
}

export function createItem(overrides = {}) {
  const body = Object.assign(
    { title: "Perf test item", description: "Created by k6", category: "electronics", tags: [] },
    overrides,
  );
  return http.post(`${BASE_URL}/api/v1/items`, JSON.stringify(body), {
    headers: JSON_HEADERS,
    tags: { name: "POST /items" },
  });
}

export function deleteItem(id) {
  return http.del(
    `${BASE_URL}/api/v1/items/${id}?caller_id=${SELLER_ID}`,
    null,
    { tags: { name: "DELETE /items/:id" } },
  );
}

export function placeHold(itemId) {
  return http.post(
    `${BASE_URL}/api/v1/items/${itemId}/hold`,
    JSON.stringify({ buyer_id: BUYER_ID }),
    { headers: JSON_HEADERS, tags: { name: "POST /items/:id/hold" } },
  );
}

export function releaseHold(itemId) {
  return http.del(
    `${BASE_URL}/api/v1/items/${itemId}/hold?caller_id=${BUYER_ID}`,
    null,
    { tags: { name: "DELETE /items/:id/hold" } },
  );
}

export function confirmHold(itemId, confirmerId) {
  return http.post(
    `${BASE_URL}/api/v1/items/${itemId}/confirm`,
    JSON.stringify({ confirmer_id: confirmerId }),
    { headers: JSON_HEADERS, tags: { name: "POST /items/:id/confirm" } },
  );
}

export function expectStatus(res, status, label) {
  check(res, { [`${label} → ${status}`]: (r) => r.status === status });
}
