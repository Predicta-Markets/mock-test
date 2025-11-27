export type MarketStatus = "OPEN" | "RESOLVED";
export type MarketOutcome = "YES" | "NO" | null;
export type OrderSide = "YES" | "NO";
export type OrderType = "BUY" | "SELL";

export interface Market {
  id: string;
  slug: string;
  question: string;
  description?: string | null;
  status: MarketStatus;
  outcome?: MarketOutcome;
  yes_price: number;
  no_price: number;
}

export interface Position {
  market_id: string;
  side: OrderSide;
  quantity: number;
  average_price: number;
  realized_pnl: number;
}

export interface OrderBookLevel {
    id: string;
    market_id: string;
    side: OrderSide;
    price: number;
    quantity: number;
}

export interface OrderRequestPayload {
  side: OrderSide;
  type: OrderType;
  price: number;
  quantity: number;
}

