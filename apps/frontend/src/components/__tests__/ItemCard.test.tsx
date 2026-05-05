import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ItemCard } from "../ItemCard";
import type { Item } from "@/lib/api";

const base: Item = {
  id: "abc-123",
  title: "Test Keyboard",
  description: "Mechanical keyboard",
  category: "electronics",
  tags: ["used"],
  status: "available",
  seller_id: "seller-1",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("ItemCard", () => {
  it("renders title and description", () => {
    render(<ItemCard item={base} />);
    expect(screen.getByText("Test Keyboard")).toBeInTheDocument();
    expect(screen.getByText("Mechanical keyboard")).toBeInTheDocument();
  });

  it("shows on-hold badge when status is on_hold", () => {
    render(<ItemCard item={{ ...base, status: "on_hold" }} />);
    expect(screen.getByText("On hold")).toBeInTheDocument();
  });

  it("shows sold badge when status is sold", () => {
    render(<ItemCard item={{ ...base, status: "sold" }} />);
    expect(screen.getByText("Sold")).toBeInTheDocument();
  });

  it("links to item detail page", () => {
    render(<ItemCard item={base} />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/items/abc-123");
  });
});
