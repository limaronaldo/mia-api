from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    cpf: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    sex: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[datetime] = mapped_column(nullable=False)
    enriched: Mapped[bool] = mapped_column(default=False, nullable=False)
    mother_name: Mapped[str] = mapped_column(nullable=True)
    father_name: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class ScoreEvaluation(Base):
    __tablename__ = "score_evaluations"
    __table_args__ = {"schema": "customers"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    score: Mapped[float] = mapped_column(default=0, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey(Customer.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class PurchasingPower(Base):
    __tablename__ = "purchasing_powers"
    __table_args__ = {"schema": "customers"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    code: Mapped[int] = mapped_column(nullable=False)
    value: Mapped[float] = mapped_column(nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey(Customer.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class Education(Base):
    __tablename__ = "educations"
    __table_args__ = {"schema": "customers"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    education: Mapped[str] = mapped_column(nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey(Customer.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = {"schema": "customers"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    license_plate: Mapped[str] = mapped_column(nullable=False)
    brand: Mapped[str] = mapped_column(nullable=True)
    renavan: Mapped[str] = mapped_column(nullable=True)
    fabrication_year: Mapped[int] = mapped_column(nullable=True)
    chassis: Mapped[str] = mapped_column(nullable=True)
    model_year: Mapped[int] = mapped_column(nullable=True)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey(Customer.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class Interest(Base):
    __tablename__ = "interests"
    __table_args__ = {"schema": "customers"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    pre_approved_personal_loan: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    pre_approved_mortgage: Mapped[bool] = mapped_column(nullable=False, default=False)
    pre_approved_vehicle_financing: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    middle_class: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_luxury_goods: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_investments: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_premium_bank_account: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    owns_credit_card: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_multiple_credit_cards: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    owns_black_credit_card: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_prime_credit_card: Mapped[bool] = mapped_column(nullable=False, default=False)
    has_accumulated_miles: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_home: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_current_accounts: Mapped[bool] = mapped_column(nullable=False, default=False)
    owns_car_insurance: Mapped[bool] = mapped_column(nullable=False, default=False)
    has_private_retirement_plan: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    personal_loan: Mapped[float] = mapped_column(nullable=False, default=0)
    vehicle_loan: Mapped[float] = mapped_column(nullable=False, default=0)
    online_shopping: Mapped[float] = mapped_column(nullable=False, default=0)
    multiple_credit_card: Mapped[float] = mapped_column(nullable=False, default=0)
    prime_credit_card: Mapped[float] = mapped_column(nullable=False, default=0)
    cable_tv: Mapped[float] = mapped_column(nullable=False, default=0)
    broadband_internet: Mapped[float] = mapped_column(nullable=False, default=0)
    own_home: Mapped[float] = mapped_column(nullable=False, default=0)
    mortgage: Mapped[float] = mapped_column(nullable=False, default=0)
    car_insurance: Mapped[float] = mapped_column(nullable=False, default=0)
    health_insurance: Mapped[float] = mapped_column(nullable=False, default=0)
    life_insurance: Mapped[float] = mapped_column(nullable=False, default=0)
    home_insurance: Mapped[float] = mapped_column(nullable=False, default=0)
    investments: Mapped[float] = mapped_column(nullable=False, default=0)
    consignment_loan: Mapped[float] = mapped_column(nullable=False, default=0)
    private_retirement_plan: Mapped[float] = mapped_column(nullable=False, default=0)
    frequent_flyer_miles_redemption: Mapped[float] = mapped_column(
        nullable=False, default=0
    )
    discount_hunting: Mapped[float] = mapped_column(nullable=False, default=0)
    fitness: Mapped[float] = mapped_column(nullable=False, default=0)
    travel: Mapped[float] = mapped_column(nullable=False, default=0)
    luxury: Mapped[float] = mapped_column(nullable=False, default=0)
    moviegoer: Mapped[float] = mapped_column(nullable=False, default=0)
    public_transportation: Mapped[float] = mapped_column(nullable=False, default=0)
    online_games: Mapped[float] = mapped_column(nullable=False, default=0)
    video_games: Mapped[float] = mapped_column(nullable=False, default=0)
    early_adopter: Mapped[float] = mapped_column(nullable=False, default=0)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey(Customer.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
