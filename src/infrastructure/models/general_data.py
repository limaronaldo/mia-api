from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.config.database import Base


class Email(Base):
    __tablename__ = "emails"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    email: Mapped[str] = mapped_column(nullable=False)
    ranking: Mapped[int] = mapped_column(nullable=False)
    is_valid: Mapped[bool] = mapped_column(nullable=True)
    quality_score: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)

    customer_emails = relationship(
        "CustomerEmail", back_populates="email", uselist=True, lazy="select"
    )
    company_emails = relationship(
        "CompanyEmail", back_populates="email", uselist=True, lazy="select"
    )


class Phone(Base):
    __tablename__ = "phones"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    ddd: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    operator: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)
    ranking: Mapped[int] = mapped_column(nullable=False, server_default="1")
    is_valid: Mapped[bool] = mapped_column(nullable=True)
    quality_score: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default="now()")

    customer_phones = relationship(
        "CustomerPhone", back_populates="phone", uselist=True, lazy="select"
    )
    company_phones = relationship(
        "CompanyPhone", back_populates="phone", uselist=True, lazy="select"
    )


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    street: Mapped[str] = mapped_column(nullable=True)
    number: Mapped[str] = mapped_column(nullable=True)
    neighborhood: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=True)
    cep: Mapped[str] = mapped_column(nullable=True)
    complement: Mapped[str] = mapped_column(nullable=True)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
    street_type: Mapped[str] = mapped_column(nullable=True)
    ranking: Mapped[int] = mapped_column(nullable=False, server_default="1")
    is_valid: Mapped[bool] = mapped_column(nullable=True)
    quality_score: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default="now()")

    customer_addresses = relationship(
        "CustomerAddress", back_populates="address", uselist=True, lazy="select"
    )
    company_addresses = relationship(
        "CompanyAddress", back_populates="address", uselist=True, lazy="select"
    )
