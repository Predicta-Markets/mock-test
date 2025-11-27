from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from typing import ClassVar

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    attributes,
    mapped_column,
    reconstructor,
    relationship,
    validates,
)

from .db import Base


class MarketStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class MarketOutcome(str, enum.Enum):
    YES = "YES"
    NO = "NO"


class OrderSide(str, enum.Enum):
    YES = "YES"
    NO = "NO"


class OrderType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


DECIMAL_CENTS = Numeric(6, 2, asdecimal=True)
DECIMAL_PNL = Numeric(14, 2, asdecimal=True)


class EnumCoercionMixin:
    """Ensures enum attributes remain Python enums while persisting strings."""

    _enum_fields: ClassVar[dict[str, type[enum.Enum]]] = {}

    @staticmethod
    def _coerce(enum_cls: type[enum.Enum], value: enum.Enum | str | None):
        if value is None or isinstance(value, enum_cls):
            return value
        return enum_cls(value)

    def _coerce_all(self) -> None:
        for attr_name, enum_cls in self._enum_fields.items():
            value = getattr(self, attr_name, None)
            if value is None or isinstance(value, enum_cls):
                continue
            attributes.set_committed_value(self, attr_name, enum_cls(value))

    @reconstructor
    def _init_on_load(self) -> None:
        self._coerce_all()

    def _convert_for_attr(self, key: str, value: enum.Enum | str | None):
        enum_cls = self._enum_fields.get(key)
        if enum_cls is None:
            return value
        return self._coerce(enum_cls, value)


class Market(EnumCoercionMixin, Base):
    __tablename__ = "markets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    question: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text())
    status: Mapped[MarketStatus] = mapped_column(
        String(16),
        default=MarketStatus.OPEN,
    )
    outcome: Mapped[MarketOutcome | None] = mapped_column(
        String(16)
    )
    yes_price: Mapped[Decimal] = mapped_column(DECIMAL_CENTS)
    no_price: Mapped[Decimal] = mapped_column(DECIMAL_CENTS)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="market", cascade="all, delete-orphan")
    positions: Mapped[list["Position"]] = relationship(back_populates="market", cascade="all, delete-orphan")
    resolution: Mapped["Resolution | None"] = relationship(back_populates="market", uselist=False)
    order_book_levels: Mapped[list["OrderBookLevel"]] = relationship(
        back_populates="market",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("yes_price + no_price = 100.00", name="ck_market_complement_prices"),
    )

    _enum_fields = {"status": MarketStatus, "outcome": MarketOutcome}

    @validates("status", "outcome")
    def _validate_market_enums(self, key: str, value):
        return self._convert_for_attr(key, value)


class Position(EnumCoercionMixin, Base):
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"))
    side: Mapped[OrderSide] = mapped_column(String(8))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    average_price: Mapped[Decimal] = mapped_column(DECIMAL_CENTS, default=Decimal("0.00"))
    realized_pnl: Mapped[Decimal] = mapped_column(DECIMAL_PNL, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    market: Mapped[Market] = relationship(back_populates="positions")

    __table_args__ = (
        UniqueConstraint("market_id", "side", name="uq_positions_market_side"),
        CheckConstraint("quantity >= 0", name="ck_positions_qty_positive"),
    )

    _enum_fields = {"side": OrderSide}

    @validates("side")
    def _validate_side(self, key: str, value):
        return self._convert_for_attr(key, value)


class Order(EnumCoercionMixin, Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"))
    side: Mapped[OrderSide] = mapped_column(String(8))
    type: Mapped[OrderType] = mapped_column(String(8))
    price: Mapped[Decimal] = mapped_column(DECIMAL_CENTS)
    quantity: Mapped[int] = mapped_column(Integer)
    resting_quantity: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[Decimal] = mapped_column(DECIMAL_PNL)
    realized_pnl: Mapped[Decimal] = mapped_column(DECIMAL_PNL, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    market: Mapped[Market] = relationship(back_populates="orders")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_orders_qty_non_negative"),
        CheckConstraint("price >= 0", name="ck_orders_price_positive"),
        CheckConstraint("resting_quantity >= 0", name="ck_orders_resting_qty_positive"),
    )

    _enum_fields = {"side": OrderSide, "type": OrderType}

    @validates("side", "type")
    def _validate_order_enums(self, key: str, value):
        return self._convert_for_attr(key, value)


class Resolution(EnumCoercionMixin, Base):
    __tablename__ = "resolutions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), unique=True)
    outcome: Mapped[MarketOutcome] = mapped_column(String(16))
    payout_yes: Mapped[Decimal] = mapped_column(DECIMAL_PNL)
    payout_no: Mapped[Decimal] = mapped_column(DECIMAL_PNL)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    market: Mapped[Market] = relationship(back_populates="resolution")

    _enum_fields = {"outcome": MarketOutcome}

    @validates("outcome")
    def _validate_resolution_outcome(self, key: str, value):
        return self._convert_for_attr(key, value)


class OrderBookLevel(EnumCoercionMixin, Base):
    __tablename__ = "order_book_levels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"))
    side: Mapped[OrderSide] = mapped_column(String(8))
    price: Mapped[Decimal] = mapped_column(DECIMAL_CENTS)
    quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    market: Mapped[Market] = relationship(back_populates="order_book_levels")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_book_levels_qty_positive"),
        CheckConstraint("price >= 0", name="ck_order_book_levels_price_positive"),
    )

    _enum_fields = {"side": OrderSide}

    @validates("side")
    def _validate_order_book_side(self, key: str, value):
        return self._convert_for_attr(key, value)

