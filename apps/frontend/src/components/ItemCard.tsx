import Link from "next/link";
import type { Item } from "@/lib/api";

export function ItemCard({ item }: { item: Item }) {
  const isOnHold = item.status === "on_hold";
  const isSold = item.status === "sold";

  return (
    <Link
      href={`/items/${item.id}`}
      className={`block rounded-xl border bg-white p-4 shadow-sm transition hover:shadow-md ${
        isOnHold ? "opacity-60" : ""
      } ${isSold ? "opacity-40 pointer-events-none" : ""}`}
    >
      <div className="flex items-start justify-between gap-2">
        <h2 className="font-semibold text-gray-900 line-clamp-1">{item.title}</h2>
        {isOnHold && (
          <span className="shrink-0 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700">
            On hold
          </span>
        )}
        {isSold && (
          <span className="shrink-0 rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-500">
            Sold
          </span>
        )}
      </div>
      <p className="mt-1 text-sm text-gray-500 line-clamp-2">{item.description}</p>
      <div className="mt-3 flex flex-wrap gap-1">
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
          {item.category.replace("_", " ")}
        </span>
        {item.tags.map((tag) => (
          <span
            key={tag}
            className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600"
          >
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
