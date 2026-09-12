from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)

    law_office_id: Mapped[int] = mapped_column(
        ForeignKey("law_offices.id"),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    contact_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
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
        back_populates="clients",
    )
    transactions = relationship(
        "Transaction",
        back_populates="client",
        cascade="all, delete-orphan",
    )
