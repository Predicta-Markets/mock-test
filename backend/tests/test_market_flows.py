from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models import MarketOutcome, MarketStatus, OrderSide, OrderType
from app.schemas import MarketCreate, OrderRequest
from app.services import markets as market_service


@pytest.mark.asyncio
async def test_buy_order_updates_position(session):
    market = await market_service.create_market(
        session,
        MarketCreate(question="Will it rain tomorrow?", description=None, slug=None, initial_price_yes=Decimal("60.00")),
    )
    await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.YES, type=OrderType.BUY, price=Decimal("60.00"), quantity=10),
    )
    positions = await market_service.get_positions(session, market.id)
    yes_position = next(p for p in positions if p.side == OrderSide.YES)
    assert yes_position.quantity == 10
    assert yes_position.average_price == Decimal("60.00")


@pytest.mark.asyncio
async def test_sell_more_than_hold_is_rejected(session):
    market = await market_service.create_market(
        session,
        MarketCreate(question="Is the sky blue?", description=None, slug=None, initial_price_yes=Decimal("55.00")),
    )
    await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.YES, type=OrderType.BUY, price=Decimal("55.00"), quantity=5),
    )

    with pytest.raises(HTTPException):
        await market_service.place_order(
            session,
            market.id,
            OrderRequest(side=OrderSide.YES, type=OrderType.SELL, price=Decimal("60.00"), quantity=10),
        )


@pytest.mark.asyncio
async def test_resolution_clears_positions(session):
    market = await market_service.create_market(
        session,
        MarketCreate(question="Will BTC close above 50k?", description=None, slug=None, initial_price_yes=Decimal("40.00")),
    )
    await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.YES, type=OrderType.BUY, price=Decimal("40.00"), quantity=5),
    )
    await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.NO, type=OrderType.BUY, price=Decimal("60.00"), quantity=5),
    )

    resolved = await market_service.resolve_market(session, market.id, MarketOutcome.YES)
    assert resolved.status == MarketStatus.RESOLVED

    positions = await market_service.get_positions(session, market.id)
    assert all(position.quantity == 0 for position in positions)


@pytest.mark.asyncio
async def test_yes_order_matches_existing_no_level(session):
    market = await market_service.create_market(
        session,
        MarketCreate(question="Will ETH flip BTC?", description=None, slug=None, initial_price_yes=Decimal("50.00")),
    )

    # Acquire NO inventory to allow resting liquidity later.
    await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.NO, type=OrderType.BUY, price=Decimal("50.00"), quantity=5),
    )

    # Post a NO sell order at 40 cents that should rest on the order book.
    sell_order = await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.NO, type=OrderType.SELL, price=Decimal("40.00"), quantity=5),
    )
    assert sell_order.quantity == 0
    assert sell_order.resting_quantity == 5

    # YES buy order should match against the NO level at 40 and trade at 60.
    yes_order = await market_service.place_order(
        session,
        market.id,
        OrderRequest(side=OrderSide.YES, type=OrderType.BUY, price=Decimal("72.00"), quantity=5),
    )
    assert yes_order.quantity == 5
    assert yes_order.price == Decimal("60.00")
    assert yes_order.resting_quantity == 0

