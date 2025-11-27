import { Market, OrderBookLevel, OrderRequestPayload, Position } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = (data as { detail?: string }).detail ?? "Request failed";
    throw new Error(detail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export function fetchMarkets(): Promise<Market[]> {
  return request<Market[]>("/markets");
}

export function fetchMarket(id: string): Promise<Market> {
  return request<Market>(`/markets/${id}`);
}

export function fetchPositions(id: string): Promise<Position[]> {
  return request<Position[]>(`/markets/${id}/positions`);
}

export function fetchOrderBook(marketId: string): Promise<OrderBookLevel[]> {
    return request<OrderBookLevel[]>(`/markets/${marketId}/order-book`);
}

export function createMarket(payload: {
  question: string;
  description?: string;
  initial_price_yes: number;
  slug?: string;
}): Promise<Market> {
  return request<Market>("/markets", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function placeOrder(marketId: string, payload: OrderRequestPayload) {
  return request(`/markets/${marketId}/orders`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function resolveMarket(marketId: string, outcome: "YES" | "NO") {
  return request(`/markets/${marketId}/resolve`, {
    method: "POST",
    body: JSON.stringify({ outcome }),
  });
}

