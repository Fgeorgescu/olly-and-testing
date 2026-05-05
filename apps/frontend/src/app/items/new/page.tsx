"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api, type ItemCategory, type ItemTag } from "@/lib/api";

const CATEGORIES: { value: ItemCategory; label: string }[] = [
  { value: "electronics", label: "Electronics" },
  { value: "furniture", label: "Furniture" },
  { value: "clothing", label: "Clothing" },
  { value: "vehicles", label: "Vehicles" },
  { value: "real_estate", label: "Real estate" },
  { value: "other", label: "Other" },
];

const TAGS: { value: ItemTag; label: string }[] = [
  { value: "used", label: "Used" },
  { value: "new", label: "New" },
  { value: "negotiable", label: "Negotiable" },
  { value: "urgent", label: "Urgent" },
];

interface FormValues {
  title: string;
  description: string;
  category: ItemCategory | "";
  tags: ItemTag[];
  seller_id: string;
}

interface FormErrors {
  title?: string;
  description?: string;
  category?: string;
  seller_id?: string;
}

function validate(values: FormValues): FormErrors {
  const errors: FormErrors = {};
  if (!values.title.trim()) errors.title = "Title is required";
  else if (values.title.length > 100) errors.title = "Max 100 characters";
  if (!values.description.trim()) errors.description = "Description is required";
  else if (values.description.length > 2000)
    errors.description = "Max 2000 characters";
  if (!values.category) errors.category = "Category is required";
  if (!values.seller_id.trim()) errors.seller_id = "Seller ID is required";
  else if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      values.seller_id,
    )
  )
    errors.seller_id = "Must be a valid UUID";
  return errors;
}

export default function PostItemPage() {
  const router = useRouter();
  const qc = useQueryClient();

  const [values, setValues] = useState<FormValues>({
    title: "",
    description: "",
    category: "",
    tags: [],
    seller_id: "",
  });
  const [touched, setTouched] = useState<Partial<Record<keyof FormValues, boolean>>>({});
  const errors = validate(values);

  const mutation = useMutation({
    mutationFn: () =>
      api.items.create({
        ...values,
        category: values.category as ItemCategory,
      }),
    onSuccess: (item) => {
      qc.invalidateQueries({ queryKey: ["items"] });
      router.push(`/items/${item.id}`);
    },
  });

  function field(name: keyof FormValues) {
    return {
      onBlur: () => setTouched((t) => ({ ...t, [name]: true })),
    };
  }

  function toggleTag(tag: ItemTag) {
    setValues((v) => ({
      ...v,
      tags: v.tags.includes(tag) ? v.tags.filter((t) => t !== tag) : [...v.tags, tag],
    }));
  }

  const hasErrors = Object.keys(errors).length > 0;

  return (
    <main className="max-w-lg mx-auto px-4 py-8 w-full">
      <button
        onClick={() => router.back()}
        className="text-sm text-blue-600 hover:underline mb-4 inline-block"
      >
        ← Back
      </button>

      <h1 className="text-2xl font-bold mb-6">Post an item</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          setTouched({ title: true, description: true, category: true, seller_id: true });
          if (!hasErrors) mutation.mutate();
        }}
        className="space-y-4"
      >
        {/* Title */}
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <input
            value={values.title}
            onChange={(e) => setValues((v) => ({ ...v, title: e.target.value }))}
            {...field("title")}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="What are you selling?"
          />
          {touched.title && errors.title && (
            <p className="mt-1 text-xs text-red-500">{errors.title}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            value={values.description}
            onChange={(e) => setValues((v) => ({ ...v, description: e.target.value }))}
            {...field("description")}
            rows={4}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="Describe the item, condition, etc."
          />
          {touched.description && errors.description && (
            <p className="mt-1 text-xs text-red-500">{errors.description}</p>
          )}
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium mb-1">Category</label>
          <select
            value={values.category}
            onChange={(e) =>
              setValues((v) => ({ ...v, category: e.target.value as ItemCategory }))
            }
            {...field("category")}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select a category</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
          {touched.category && errors.category && (
            <p className="mt-1 text-xs text-red-500">{errors.category}</p>
          )}
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium mb-2">Tags</label>
          <div className="flex flex-wrap gap-2">
            {TAGS.map((t) => (
              <button
                key={t.value}
                type="button"
                onClick={() => toggleTag(t.value)}
                className={`rounded-full px-3 py-1 text-sm border transition ${
                  values.tags.includes(t.value)
                    ? "bg-blue-600 text-white border-blue-600"
                    : "text-gray-600 border-gray-300 hover:border-blue-400"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Seller ID */}
        <div>
          <label className="block text-sm font-medium mb-1">Seller ID</label>
          <input
            value={values.seller_id}
            onChange={(e) => setValues((v) => ({ ...v, seller_id: e.target.value }))}
            {...field("seller_id")}
            className="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          />
          {touched.seller_id && errors.seller_id && (
            <p className="mt-1 text-xs text-red-500">{errors.seller_id}</p>
          )}
        </div>

        {mutation.isError && (
          <p className="text-sm text-red-500">
            {(mutation.error as Error).message}
          </p>
        )}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40"
        >
          {mutation.isPending ? "Posting…" : "Post item"}
        </button>
      </form>
    </main>
  );
}
