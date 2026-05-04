"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();

  const { data: item, isLoading, isError } = useQuery({
    queryKey: ["items", id],
    queryFn: () => api.items.get(id),
  });

  const [buyerId, setBuyerId] = useState("");
  const [callerId, setCallerId] = useState("");
  const [holdInfo, setHoldInfo] = useState<{ sellerContact: string } | null>(null);
  const placeMutation = useMutation({
    mutationFn: () => api.holds.place(id, buyerId),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["items", id] });
      setHoldInfo({ sellerContact: data.seller_contact ?? "Contact not available" });
    },
  });

  const releaseMutation = useMutation({
    mutationFn: () => api.holds.release(id, callerId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["items", id] });
      setHoldInfo(null);
    },
  });

  const confirmMutation = useMutation({
    mutationFn: () => api.holds.confirm(id, callerId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["items", id] });
    },
  });

  if (isLoading) return <p className="p-8 text-center text-gray-500">Loading…</p>;
  if (isError || !item)
    return <p className="p-8 text-center text-red-500">Item not found.</p>;

  return (
    <main className="max-w-2xl mx-auto px-4 py-8 w-full">
      <button
        onClick={() => router.back()}
        className="text-sm text-blue-600 hover:underline mb-4 inline-block"
      >
        ← Back
      </button>

      <div className="bg-white rounded-xl border shadow-sm p-6">
        <div className="flex items-start justify-between gap-4">
          <h1 className="text-2xl font-bold text-gray-900">{item.title}</h1>
          {item.status === "on_hold" && (
            <span className="shrink-0 rounded-full bg-yellow-100 px-3 py-1 text-sm font-medium text-yellow-700">
              On hold
            </span>
          )}
          {item.status === "sold" && (
            <span className="shrink-0 rounded-full bg-gray-200 px-3 py-1 text-sm font-medium text-gray-500">
              Sold
            </span>
          )}
        </div>

        <p className="mt-3 text-gray-600">{item.description}</p>

        <div className="mt-4 flex flex-wrap gap-2">
          <span className="rounded bg-gray-100 px-2 py-1 text-sm text-gray-600">
            {item.category.replace("_", " ")}
          </span>
          {item.tags.map((tag) => (
            <span
              key={tag}
              className="rounded bg-blue-50 px-2 py-1 text-sm text-blue-600"
            >
              {tag}
            </span>
          ))}
        </div>

        <p className="mt-4 text-xs text-gray-400">
          Listed {new Date(item.created_at).toLocaleDateString()}
        </p>

        {/* Purchase / hold actions */}
        {item.status === "available" && (
          <div className="mt-6 border-t pt-6">
            <h2 className="font-semibold mb-3">Place hold</h2>
            <input
              placeholder="Your buyer ID (UUID)"
              value={buyerId}
              onChange={(e) => setBuyerId(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              disabled={!buyerId || placeMutation.isPending}
              onClick={() => placeMutation.mutate()}
              className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40"
            >
              {placeMutation.isPending ? "Placing…" : "Place hold"}
            </button>
            {placeMutation.isError && (
              <p className="mt-2 text-sm text-red-500">
                {(placeMutation.error as Error).message}
              </p>
            )}
          </div>
        )}

        {holdInfo && (
          <div className="mt-4 rounded-lg bg-green-50 border border-green-200 p-4">
            <p className="text-sm font-semibold text-green-800">Hold placed!</p>
            <p className="text-sm text-green-700 mt-1">
              Seller contact: <span className="font-mono">{holdInfo.sellerContact}</span>
            </p>
            <p className="mt-2 text-xs text-green-600">
              Both you and the seller must confirm once the sale is completed in
              person.
            </p>
          </div>
        )}

        {item.status === "on_hold" && (
          <div className="mt-6 border-t pt-6 space-y-3">
            <h2 className="font-semibold">Hold actions</h2>
            <input
              placeholder="Your ID (buyer or seller UUID)"
              value={callerId}
              onChange={(e) => setCallerId(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <button
                disabled={!callerId || confirmMutation.isPending}
                onClick={() => confirmMutation.mutate()}
                className="flex-1 bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-40"
              >
                {confirmMutation.isPending ? "Confirming…" : "Confirm sale"}
              </button>
              <button
                disabled={!callerId || releaseMutation.isPending}
                onClick={() => {
                  if (confirm("Release this hold?")) releaseMutation.mutate();
                }}
                className="flex-1 border border-red-300 text-red-600 py-2 rounded-lg text-sm font-medium hover:bg-red-50 disabled:opacity-40"
              >
                {releaseMutation.isPending ? "Releasing…" : "Release hold"}
              </button>
            </div>
            {confirmMutation.isError && (
              <p className="text-sm text-red-500">
                {(confirmMutation.error as Error).message}
              </p>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

