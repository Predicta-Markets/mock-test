from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from .models import MarketOutcome, MarketStatus, OrderSide, OrderType


class MarketBase(BaseModel):
    question: str = Field(min_length=4, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class MarketCreate(MarketBase):
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    initial_price_yes: Decimal = Field(gt=0, lt=100)


class MarketResponse(MarketBase):
    id: UUID
    slug: str
    status: MarketStatus
    outcome: MarketOutcome | None
    yes_price: Decimal
    no_price: Decimal

    class Config:
        from_attributes = True


class OrderRequest(BaseModel):
    side: OrderSide
    type: OrderType
    price: Decimal = Field(ge=0, le=100)
    quantity: int = Field(gt=0, le=1_000_000)


class OrderResponse(BaseModel):
    id: UUID
    market_id: UUID
    side: OrderSide
    type: OrderType
    price: Decimal
    quantity: int
    resting_quantity: int
    total_cost: Decimal
    realized_pnl: Decimal

    class Config:
        from_attributes = True


class ResolveRequest(BaseModel):
    outcome: MarketOutcome


class PositionSummary(BaseModel):
    market_id: UUID
    side: OrderSide
    quantity: int
    average_price: Decimal
    realized_pnl: Decimal

    class Config:
        from_attributes = True


class OrderBookLevelResponse(BaseModel):
    id: UUID
    market_id: UUID
    side: OrderSide
    price: Decimal
    quantity: int

    class Config:
        from_attributes = True

