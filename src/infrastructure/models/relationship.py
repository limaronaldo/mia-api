from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.config.database import Base
from src.infrastructure.models.general_data import Address, Email, Phone

if TYPE_CHECKING:
    from .public import Broker, DBProperty, Iptu


class CustomerCompany(Base):
    __tablename__ = "customer_companies"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(nullable=True)
    entry_date: Mapped[datetime] = mapped_column(nullable=True)
    exit_date: Mapped[datetime] = mapped_column(nullable=True)
    cnpj: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class CustomerEmail(Base):
    __tablename__ = "customer_emails"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        server_default="gen_random_uuid()",
    )
    email_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.emails.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    email: Mapped["Email"] = relationship(
        "Email",
        back_populates="customer_emails",
        uselist=False,
        lazy="select",
    )


class CustomerPhone(Base):
    __tablename__ = "customer_phones"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    phone_id: Mapped[UUID] = mapped_column(
        ForeignKey(Phone.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    phone: Mapped[Phone] = relationship(
        "Phone",
        back_populates="customer_phones",
        uselist=False,
        lazy="select",
    )


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey(Address.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    address: Mapped[Address] = relationship(
        "Address",
        back_populates="customer_addresses",
        uselist=False,
        lazy="select",
    )


class CompanyEmail(Base):
    __tablename__ = "company_emails"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        server_default="gen_random_uuid()",
    )
    email_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.emails.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    email: Mapped["Email"] = relationship(
        "Email",
        back_populates="company_emails",
        uselist=False,
        lazy="select",
    )


class CompanyPhone(Base):
    __tablename__ = "company_phones"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    phone_id: Mapped[UUID] = mapped_column(
        ForeignKey(Phone.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    phone: Mapped[Phone] = relationship(
        "Phone",
        back_populates="company_phones",
        uselist=False,
        lazy="select",
    )


class CompanyAddress(Base):
    __tablename__ = "company_addresses"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey(Address.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    address: Mapped[Address] = relationship(
        "Address",
        back_populates="company_addresses",
        uselist=False,
        lazy="select",
    )


class CustomerParent(Base):
    __tablename__ = "customer_parents"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    relation: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class IptuContributor(Base):
    __tablename__ = "iptu_contributor"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    contributor_number: Mapped[str] = mapped_column(
        ForeignKey("public.iptus.contributor_number"), nullable=False
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.customers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    exercise_year: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    iptu: Mapped["Iptu"] = relationship(
        "Iptu",
        back_populates="contributor",
        uselist=False,
        lazy="select",
        primaryjoin="IptuContributor.contributor_number == Iptu.contributor_number",
    )


class BrokerProperty(Base):
    __tablename__ = "broker_properties"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    broker_cod: Mapped[str] = mapped_column(
        ForeignKey("public.brokers.cod", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    property_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.immobiles.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(nullable=False)
    seq: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)

    broker: Mapped["Broker"] = relationship(
        "Broker", back_populates="properties", uselist=False, lazy="select"
    )

    property: Mapped["DBProperty"] = relationship(
        "DBProperty", back_populates="broker_properties", uselist=False, lazy="joined"
    )


class BrokerRole(Base):
    __tablename__ = "broker_roles"
    __table_args__ = {"schema": "relationships"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()"
    )
    broker_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.brokers.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)


class UserThread(Base):
    __tablename__ = "user_threads"
    __table_args__ = {"schema": "relationships"}

    user_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        nullable=False,
    )
    thread_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="gen_random_uuid()", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default="now()", nullable=False)
