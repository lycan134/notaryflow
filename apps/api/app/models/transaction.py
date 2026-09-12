from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    law_office_id: Mapped[int] = mapped_column(
        ForeignKey("law_offices.id"),
        nullable=False,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="DRAFT",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    date_received: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_completed: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    law_office = relationship(
        "LawOffice",
        back_populates="transactions",
    )

    client = relationship(
        "Client",
        back_populates="transactions",
    )