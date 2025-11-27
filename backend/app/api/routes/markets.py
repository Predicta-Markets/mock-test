from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...schemas import (
    MarketCreate,
    MarketResponse,
    OrderBookLevelResponse,
    OrderRequest,
    OrderResponse,
    PositionSummary,
    ResolveRequest,
)
from ...services import markets as market_service

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=List[MarketResponse])
async def list_markets(session: AsyncSession = Depends(get_session)) -> List[MarketResponse]:
    markets = await market_service.list_markets(session)
    return list(markets)


@router.post("", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
async def create_market(payload: MarketCreate, session: AsyncSession = Depends(get_session)) -> MarketResponse:
    return await market_service.create_market(session, payload)


@router.get("/{market_id}", response_model=MarketResponse)
async def fetch_market(market_id: UUID, session: AsyncSession = Depends(get_session)) -> MarketResponse:
    return await market_service.get_market(session, market_id)


@router.post("/{market_id}/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    market_id: UUID,
    payload: OrderRequest,
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    return await market_service.place_order(session, market_id, payload)


@router.post("/{market_id}/resolve", response_model=MarketResponse)
async def resolve_market(
    market_id: UUID,
    payload: ResolveRequest,
    session: AsyncSession = Depends(get_session),
) -> MarketResponse:
    return await market_service.resolve_market(session, market_id, payload.outcome)


@router.get("/{market_id}/positions", response_model=List[PositionSummary])
async def get_positions(
    market_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> List[PositionSummary]:
    positions = await market_service.get_positions(session, market_id)
    return [PositionSummary.model_validate(pos) for pos in positions]


@router.get("/{market_id}/order-book", response_model=List[OrderBookLevelResponse])
async def get_order_book(
    market_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> List[OrderBookLevelResponse]:
    levels = await market_service.get_order_book_levels(session, market_id)
    return [OrderBookLevelResponse.model_validate(level) for level in levels]

