"use client";

import { useQuery } from "@tanstack/react-query";
import { useQueryState, parseAsString, parseAsInteger } from "nuqs";
import Link from "next/link";
import { api, type ItemCategory } from "@/lib/api";
import { ItemCard } from "@/components/ItemCard";

const CATEGORIES: ItemCategory[] = [
  "electronics",
  "furniture",
  "clothing",
  "vehicles",
  "real_estate",
  "other",
];

export default function HomePage() {
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [category, setCategory] = useQueryState(
    "category",
    parseAsString.withDefault(""),
  );
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));

  const { data, isLoading, isError } = useQuery({
    queryKey: ["items", { q, category, page }],
    queryFn: () =>
      api.items.list({
        q: q || undefined,
        category: (category as ItemCategory) || undefined,
        page,
        limit: 20,
      }),
  });

  return (
    <main className="max-w-5xl mx-auto px-4 py-8 w-full">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Marketplace</h1>
        <Link
          href="/items/new"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          Post item
        </Link>
      </div>

      {/* Search + filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <input
          type="search"
          placeholder="Search items…"
          value={q}
          onChange={(e) => {
            setQ(e.target.value || null);
            setPage(null);
          }}
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value || null);
            setPage(null);
          }}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c.replace("_", " ")}
            </option>
          ))}
        </select>
      </div>

      {/* Results */}
      {isLoading && (
        <p className="text-center text-gray-500 py-12">Loading…</p>
      )}
      {isError && (
        <p className="text-center text-red-500 py-12">
          Failed to load items. Is the backend running?
        </p>
      )}
      {data && (
        <>
          <p className="text-sm text-gray-500 mb-4">
            {data.total} item{data.total !== 1 ? "s" : ""}
          </p>
          {data.items.length === 0 ? (
            <p className="text-center text-gray-500 py-12">No items found.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {data.total > 20 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1 rounded border text-sm disabled:opacity-40"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-600">
                Page {page} of {Math.ceil(data.total / 20)}
              </span>
              <button
                disabled={page >= Math.ceil(data.total / 20)}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1 rounded border text-sm disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </main>
  );
}
