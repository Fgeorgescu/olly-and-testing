const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ItemCategory =
  | "electronics"
  | "furniture"
  | "clothing"
  | "vehicles"
  | "real_estate"
  | "other";

export type ItemTag = "used" | "new" | "negotiable" | "urgent";

export type ItemStatus = "available" | "on_hold" | "sold";

export interface Item {
  id: string;
  title: string;
  description: string;
  category: ItemCategory;
  tags: ItemTag[];
  status: ItemStatus;
  seller_id: string;
  created_at: string;
  updated_at: string;
}

export interface ItemListResponse {
  items: Item[];
  total: number;
  page: number;
  limit: number;
}

export interface HoldResponse {
  item_id: string;
  held_by: string;
  buyer_confirmed: boolean;
  seller_confirmed: boolean;
  created_at: string;
  seller_contact: string | null;
}

export interface ConfirmResponse {
  id: string;
  status: ItemStatus;
}

export interface HoldReleaseResponse {
  id: string;
  status: ItemStatus;
}

export interface ItemCreate {
  title: string;
  description: string;
  category: ItemCategory;
  tags: ItemTag[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  items: {
    list(params: {
      q?: string;
      category?: ItemCategory;
      tags?: ItemTag[];
      page?: number;
      limit?: number;
    }): Promise<ItemListResponse> {
      const sp = new URLSearchParams();
      if (params.q) sp.set("q", params.q);
      if (params.category) sp.set("category", params.category);
      params.tags?.forEach((t) => sp.append("tags", t));
      if (params.page != null) sp.set("page", String(params.page));
      if (params.limit != null) sp.set("limit", String(params.limit));
      return request(`/api/v1/items?${sp}`);
    },
    get(id: string): Promise<Item> {
      return request(`/api/v1/items/${id}`);
    },
    create(data: ItemCreate): Promise<Item> {
      return request("/api/v1/items", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
  },
  holds: {
    place(itemId: string, buyerId: string): Promise<HoldResponse> {
      return request(`/api/v1/items/${itemId}/hold`, {
        method: "POST",
        body: JSON.stringify({ buyer_id: buyerId }),
      });
    },
    release(itemId: string, callerId: string): Promise<HoldReleaseResponse> {
      return request(
        `/api/v1/items/${itemId}/hold?caller_id=${callerId}`,
        { method: "DELETE" },
      );
    },
    confirm(itemId: string, confirmerId: string): Promise<ConfirmResponse> {
      return request(`/api/v1/items/${itemId}/confirm`, {
        method: "POST",
        body: JSON.stringify({ confirmer_id: confirmerId }),
      });
    },
  },
};
