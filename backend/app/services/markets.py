from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import (
    Market,
    MarketOutcome,
    MarketStatus,
    Order,
    OrderBookLevel,
    OrderSide,
    OrderType,
    Position,
    Resolution,
)
from ..schemas import MarketCreate, OrderRequest

HUNDRED = Decimal("100.00")
CENT = Decimal("0.01")


def _quantize(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


async def list_markets(session: AsyncSession) -> Sequence[Market]:
    result = await session.execute(select(Market).order_by(Market.created_at.desc()))
    return result.scalars().all()


async def get_market(session: AsyncSession, market_id: UUID) -> Market:
    result = await session.execute(
        select(Market)
        .options(selectinload(Market.positions))
        .where(Market.id == market_id)
    )
    market = result.scalars().first()
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return market


async def create_market(session: AsyncSession, payload: MarketCreate) -> Market:
    if payload.slug:
        if await _slug_exists(session, payload.slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already in use.")
        slug = payload.slug
    else:
        slug = await _generate_unique_slug(session, payload.question)
    price_yes = _quantize(payload.initial_price_yes)
    if price_yes <= 0 or price_yes >= HUNDRED:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Yes price must be between 0 and 100.")

    market = Market(
        slug=slug,
        question=payload.question,
        description=payload.description,
        yes_price=price_yes,
        no_price=_quantize(HUNDRED - price_yes),
    )
    session.add(market)
    await session.flush()

    for side in OrderSide:
        session.add(
            Position(
                market_id=market.id,
                side=side,
                quantity=0,
                average_price=_quantize(Decimal("0.00")),
                realized_pnl=_quantize(Decimal("0.00")),
            )
        )

    await session.commit()
    await session.refresh(market)
    return market


async def place_order(session: AsyncSession, market_id: UUID, payload: OrderRequest) -> Order:
    market = await get_market(session, market_id)
    if market.status != MarketStatus.OPEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Market is resolved.")

    limit_price = _quantize(payload.price)
    complement = _quantize(HUNDRED - limit_price)
    if complement < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Price must be <= 100.")

    position = await _get_position(session, market_id, payload.side)
    if payload.type == OrderType.SELL and payload.quantity > position.quantity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot sell more contracts than currently held.",
        )

    comp_side = OrderSide.NO if payload.side == OrderSide.YES else OrderSide.YES
    target_price = complement

    remaining_qty = payload.quantity
    executed_qty = 0
    executed_cost = Decimal("0.00")
    realized_total = Decimal("0.00")

    while remaining_qty > 0:
        level = await _get_best_level(session, market_id, comp_side, target_price)
        if not level:
            break

        fill_qty = min(remaining_qty, level.quantity)
        actual_price = _calculate_trade_price(payload.side, level.price)
        realized = _apply_trade(position, payload.type, actual_price, fill_qty)
        executed_qty += fill_qty
        executed_cost += actual_price * fill_qty
        realized_total += realized
        remaining_qty -= fill_qty

        await _consume_level(session, level, fill_qty)
        _update_market_price_from_fill(market, payload.side, actual_price)

    resting_qty = 0
    if remaining_qty > 0:
        if payload.type == OrderType.BUY:
            realized = _apply_trade(position, OrderType.BUY, limit_price, remaining_qty)
            executed_qty += remaining_qty
            executed_cost += limit_price * remaining_qty
            realized_total += realized
            _update_market_price_from_fill(market, payload.side, limit_price)
            remaining_qty = 0
        else:
            resting_qty = remaining_qty
            await _add_order_book_level(session, market.id, payload.side, limit_price, resting_qty)
            remaining_qty = 0

    if executed_qty == 0:
        # No fills occurred; market price remains unchanged.
        order_price = limit_price
    else:
        order_price = _quantize(executed_cost / Decimal(executed_qty))

    order = Order(
        market_id=market_id,
        side=payload.side,
        type=payload.type,
        price=order_price,
        quantity=executed_qty,
        resting_quantity=resting_qty,
        total_cost=_quantize(executed_cost),
        realized_pnl=_quantize(realized_total),
    )
    session.add(order)

    await session.commit()
    await session.refresh(order)
    return order


async def resolve_market(session: AsyncSession, market_id: UUID, outcome: MarketOutcome) -> Market:
    market = await get_market(session, market_id)
    if market.status == MarketStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Market already resolved.")

    payout_yes = Decimal("0.00")
    payout_no = Decimal("0.00")

    positions = await _get_positions(session, market_id)
    for position in positions:
        winning = position.side.value == outcome.value
        payout_price = HUNDRED if winning else Decimal("0.00")
        pnl = (payout_price - position.average_price) * Decimal(position.quantity)
        position.realized_pnl = _quantize(position.realized_pnl + pnl)
        if position.side == OrderSide.YES:
            payout_yes = _quantize(payout_price * Decimal(position.quantity))
        else:
            payout_no = _quantize(payout_price * Decimal(position.quantity))
        position.quantity = 0
        position.average_price = _quantize(Decimal("0.00"))

    market.status = MarketStatus.RESOLVED
    market.outcome = outcome
    resolution = Resolution(
        market_id=market.id,
        outcome=outcome,
        payout_yes=payout_yes,
        payout_no=payout_no,
    )
    session.add(resolution)
    await session.commit()
    await session.refresh(market)
    return market


async def get_positions(session: AsyncSession, market_id: UUID) -> Sequence[Position]:
    positions = await _get_positions(session, market_id)
    return positions


async def get_order_book_levels(session: AsyncSession, market_id: UUID) -> list[OrderBookLevel]:
    stmt = (
        select(OrderBookLevel)
        .where(OrderBookLevel.market_id == market_id)
        .order_by(OrderBookLevel.side.asc(), OrderBookLevel.price.asc(), OrderBookLevel.created_at.asc())
    )
    result = await session.execute(stmt)
    # Return ORM instances so pydantic can leverage `from_attributes`.
    return list(result.scalars().all())


async def _generate_unique_slug(session: AsyncSession, question: str) -> str:
    base = _slugify(question)
    slug = base
    idx = 1
    while await _slug_exists(session, slug):
        slug = f"{base}-{idx}"
        idx += 1
    return slug


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "market"


async def _slug_exists(session: AsyncSession, slug: str) -> bool:
    result = await session.execute(select(func.count(Market.id)).where(Market.slug == slug))
    count = result.scalar_one()
    return count > 0


async def _get_position(session: AsyncSession, market_id: UUID, side: OrderSide) -> Position:
    result = await session.execute(
        select(Position).where(Position.market_id == market_id, Position.side == side)
    )
    position = result.scalars().first()
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
    return position


async def _get_positions(session: AsyncSession, market_id: UUID) -> list[Position]:
    result = await session.execute(select(Position).where(Position.market_id == market_id).order_by(Position.side))
    return list(result.scalars().all())


def _apply_trade(position: Position, order_type: OrderType, price: Decimal, quantity: int) -> Decimal:
    price = _quantize(price)
    qty_decimal = Decimal(quantity)
    realized = Decimal("0.00")

    if order_type == OrderType.BUY:
        new_qty = position.quantity + quantity
        numerator = (Decimal(position.quantity) * position.average_price) + (qty_decimal * price)
        average_price = numerator / Decimal(new_qty) if new_qty else Decimal("0.00")
        position.quantity = new_qty
        position.average_price = _quantize(average_price if new_qty else Decimal("0.00"))
    else:
        realized = (price - position.average_price) * qty_decimal
        position.quantity -= quantity
        position.realized_pnl = _quantize(position.realized_pnl + realized)
        if position.quantity == 0:
            position.average_price = _quantize(Decimal("0.00"))

    return _quantize(realized)


async def _get_best_level(
    session: AsyncSession,
    market_id: UUID,
    side: OrderSide,
    min_price: Decimal,
) -> OrderBookLevel | None:
    stmt = (
        select(OrderBookLevel)
        .where(
            OrderBookLevel.market_id == market_id,
            OrderBookLevel.side == side,
            OrderBookLevel.price >= min_price,
        )
        .order_by(OrderBookLevel.price.asc(), OrderBookLevel.created_at.asc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def _consume_level(session: AsyncSession, level: OrderBookLevel, quantity: int) -> None:
    level.quantity -= quantity
    if level.quantity <= 0:
        await session.delete(level)
    else:
        session.add(level)
    await session.flush()


async def _add_order_book_level(
    session: AsyncSession,
    market_id: UUID,
    side: OrderSide,
    price: Decimal,
    quantity: int,
) -> None:
    level = OrderBookLevel(
        market_id=market_id,
        side=side,
        price=_quantize(price),
        quantity=quantity,
    )
    session.add(level)


def _calculate_trade_price(order_side: OrderSide, level_price: Decimal) -> Decimal:
    return _quantize(HUNDRED - level_price)


def _update_market_price_from_fill(market: Market, order_side: OrderSide, fill_price: Decimal) -> None:
    if order_side == OrderSide.YES:
        market.yes_price = fill_price
        market.no_price = _quantize(HUNDRED - fill_price)
    else:
        yes_price = _quantize(HUNDRED - fill_price)
        market.yes_price = yes_price
        market.no_price = fill_price

