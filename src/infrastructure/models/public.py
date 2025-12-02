import uuid
from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.config.database import Base

from .files import IptuFile

# if TYPE_CHECKING:
from .relationship import BrokerProperty, BrokerRole, IptuContributor


class Iptu(Base):
    __tablename__ = "iptus"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    contributor_number: Mapped[str] = mapped_column(String, nullable=False)
    exercise_year: Mapped[float] = mapped_column(
        Float, server_default=text("'-1'::double precision")
    )
    registration_date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=False))
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )

    infos: Mapped["IptuInfos"] = relationship(
        "IptuInfos", back_populates="iptu", lazy="select", uselist=False
    )
    areas: Mapped["IptuAreas"] = relationship(
        "IptuAreas", back_populates="iptu", lazy="select", uselist=False
    )
    locations: Mapped["IptuLocations"] = relationship(
        "IptuLocations", back_populates="iptu", lazy="select", uselist=False
    )

    contributor: Mapped[list["IptuContributor"]] = relationship(
        "IptuContributor",
        back_populates="iptu",
        lazy="select",
        uselist=True,
        primaryjoin="IptuContributor.contributor_number == Iptu.contributor_number",
    )

    files: Mapped[list["IptuFile"]] = relationship(
        "IptuFile",
        back_populates="iptu",
        lazy="select",
        uselist=True,
        primaryjoin="IptuFile.contributor_number == Iptu.contributor_number",
    )


class IptuInfos(Base):
    __tablename__ = "iptu_infos"
    __table_args__ = {"schema": "public"}

    iptu_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public.iptus.id"),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    floors_quantity: Mapped[float] = mapped_column(Float)
    obsolescence_factor: Mapped[float] = mapped_column(Float)
    contributor_life_start_year: Mapped[float] = mapped_column(Float)
    contributor_life_start_month: Mapped[float] = mapped_column(Float)
    contributor_phase: Mapped[float] = mapped_column(Float)
    nl_number: Mapped[float] = mapped_column(Float)
    corrected_construction_year: Mapped[float] = mapped_column(Float)

    iptu: Mapped["Iptu"] = relationship("Iptu", back_populates="infos", lazy="select")


class IptuAreas(Base):
    __tablename__ = "iptu_areas"
    __table_args__ = {"schema": "public"}

    iptu_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public.iptus.id"),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    land_area: Mapped[float] = mapped_column(Float)
    built_area: Mapped[float] = mapped_column(Float)
    occupied_area: Mapped[float] = mapped_column(Float)
    land_m2_value: Mapped[float] = mapped_column(Float)
    construction_m2_value: Mapped[float] = mapped_column(Float)
    land_type: Mapped[str] = mapped_column(String)
    calculation_frontage: Mapped[float] = mapped_column(Float)
    construction_standard_type: Mapped[str] = mapped_column(String)
    corners_fronts_quantity: Mapped[float] = mapped_column(Float)
    ideal_fraction: Mapped[float] = mapped_column(Float)

    iptu: Mapped["Iptu"] = relationship("Iptu", back_populates="areas", lazy="select")


class IptuLocations(Base):
    __tablename__ = "iptu_locations"
    __table_args__ = {"schema": "public"}

    iptu_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public.iptus.id"),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    property_codlog: Mapped[str] = mapped_column(String)
    property_street_name: Mapped[str] = mapped_column(String)
    property_number: Mapped[str] = mapped_column(String)
    property_complement: Mapped[str] = mapped_column(String)
    property_neighborhood: Mapped[str] = mapped_column(String)
    property_postal_code: Mapped[str] = mapped_column(String)
    property_reference: Mapped[str] = mapped_column(String)
    property_usage_type: Mapped[str] = mapped_column(String)
    condominium_number: Mapped[str] = mapped_column(String)

    iptu: Mapped["Iptu"] = relationship(
        "Iptu", back_populates="locations", lazy="select"
    )


class Photo(Base):
    __tablename__ = "photos"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    ref: Mapped[str] = mapped_column(ForeignKey("public.immobiles.ref"), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String)
    src: Mapped[dict] = mapped_column(JSON, nullable=False)
    featured: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now()
    )
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    imagekit_id: Mapped[Optional[str]] = mapped_column(String)

    property: Mapped["DBProperty"] = relationship(
        "DBProperty", back_populates="photos", lazy="select"
    )


class DBProperty(Base):
    __tablename__ = "immobiles"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, server_default="gen_random_uuid()"
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ref: Mapped[Optional[str]] = mapped_column(String(12), unique=True)
    agency_code: Mapped[Optional[str]] = mapped_column(String)
    property_type_code: Mapped[Optional[int]] = mapped_column(Integer)
    property_type: Mapped[Optional[str]] = mapped_column(String)
    business_type_code: Mapped[Optional[str]] = mapped_column(String(1))
    use_type_code: Mapped[Optional[str]] = mapped_column(String(1))
    origin_type_code: Mapped[Optional[int]] = mapped_column(Integer)
    is_launch: Mapped[Optional[int]] = mapped_column(Integer)
    zip_code: Mapped[Optional[str]] = mapped_column(String)
    street_name: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(String)
    number: Mapped[Optional[str]] = mapped_column(String)
    sql_id: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(Geometry)
    reference: Mapped[Optional[str]] = mapped_column(Text)
    city_code: Mapped[Optional[int]] = mapped_column(Integer)
    city: Mapped[Optional[str]] = mapped_column(String)
    state: Mapped[Optional[str]] = mapped_column(String(2))
    region: Mapped[Optional[str]] = mapped_column(String)
    neighborhood: Mapped[Optional[str]] = mapped_column(String)
    neighborhood_code: Mapped[Optional[int]] = mapped_column(Integer)
    region_code1: Mapped[Optional[str]] = mapped_column(String)
    region_code2: Mapped[Optional[str]] = mapped_column(String)
    region_code3: Mapped[Optional[str]] = mapped_column(String)
    value: Mapped[Optional[float]] = mapped_column(Float)
    is_for_sale: Mapped[Optional[int]] = mapped_column(SmallInteger)
    sale_value: Mapped[Optional[float]] = mapped_column(Float)
    sale_value_per_m2: Mapped[Optional[float]] = mapped_column(Float)
    is_for_rent: Mapped[Optional[int]] = mapped_column(SmallInteger)
    rent_value: Mapped[Optional[float]] = mapped_column(Float)
    rent_value_per_m2: Mapped[Optional[float]] = mapped_column(Float)
    condo_fee: Mapped[Optional[float]] = mapped_column(Float)
    iptu: Mapped[Optional[float]] = mapped_column(Float)
    bedrooms: Mapped[Optional[int]] = mapped_column(SmallInteger)
    suites: Mapped[Optional[int]] = mapped_column(SmallInteger)
    parking_spaces: Mapped[Optional[int]] = mapped_column(SmallInteger)
    total_area: Mapped[Optional[int]] = mapped_column(Integer)
    usable_area: Mapped[Optional[int]] = mapped_column(Integer)
    size: Mapped[Optional[str]] = mapped_column(String(20))
    promotion: Mapped[Optional[str]] = mapped_column(String)
    unit_details: Mapped[Optional[str]] = mapped_column(String)
    condo_details: Mapped[Optional[str]] = mapped_column(String)
    tag: Mapped[Optional[str]] = mapped_column(String)
    with_photos: Mapped[Optional[int]] = mapped_column(SmallInteger)
    with_text: Mapped[Optional[int]] = mapped_column(SmallInteger)
    with_financing: Mapped[Optional[int]] = mapped_column(SmallInteger)
    entry_value: Mapped[Optional[float]] = mapped_column(Float)
    installment_value: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[Optional[int]] = mapped_column(Integer)
    living_rooms: Mapped[Optional[int]] = mapped_column(SmallInteger)
    professional_code: Mapped[Optional[str]] = mapped_column(String)
    development: Mapped[Optional[str]] = mapped_column(String)
    complement: Mapped[Optional[str]] = mapped_column(String)
    video: Mapped[Optional[str]] = mapped_column(String)
    payment_conditions: Mapped[Optional[str]] = mapped_column(Text)
    surroundings: Mapped[Optional[str]] = mapped_column(String)
    classification_code: Mapped[Optional[int]] = mapped_column(Integer)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer)
    exclusivity: Mapped[Optional[int]] = mapped_column(SmallInteger)
    on_call: Mapped[Optional[int]] = mapped_column(SmallInteger)
    remaining: Mapped[Optional[int]] = mapped_column(SmallInteger)
    accepts_swap: Mapped[Optional[int]] = mapped_column(SmallInteger)
    has_income: Mapped[Optional[int]] = mapped_column(SmallInteger)
    building_name: Mapped[Optional[str]] = mapped_column(String)
    title: Mapped[Optional[str]] = mapped_column(Text)
    new_title: Mapped[Optional[str]] = mapped_column(Text)
    print_text: Mapped[Optional[str]] = mapped_column(String)
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    publication_agency_code: Mapped[Optional[str]] = mapped_column(String)
    photo_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    iptu_type: Mapped[Optional[str]] = mapped_column(String)
    system_rule: Mapped[Optional[str]] = mapped_column(String)
    photo_change_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    property_status: Mapped[Optional[str]] = mapped_column(String)
    registration_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    available_for_seasonal_rental: Mapped[Optional[int]] = mapped_column(SmallInteger)
    seasonal_rental_value: Mapped[Optional[float]] = mapped_column(Float)
    capacity: Mapped[Optional[int]] = mapped_column(Integer)
    disabled_property: Mapped[Optional[int]] = mapped_column(SmallInteger)
    rental_period: Mapped[Optional[str]] = mapped_column(String)
    furniture_status: Mapped[Optional[str]] = mapped_column(String)
    unit_features: Mapped[Optional[str]] = mapped_column(String)
    condo_features: Mapped[Optional[str]] = mapped_column(String)
    previous_code: Mapped[Optional[str]] = mapped_column(String)
    development_photo_change_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    residential: Mapped[Optional[str]] = mapped_column(String(1))
    commercial: Mapped[Optional[str]] = mapped_column(String(1))
    rural: Mapped[Optional[str]] = mapped_column(String(1))
    industrial: Mapped[Optional[str]] = mapped_column(String(1))
    simplified_type_code: Mapped[Optional[int]] = mapped_column(Integer)
    simplified_type: Mapped[Optional[str]] = mapped_column(String)
    elevator_quantity: Mapped[Optional[int]] = mapped_column(Integer)
    commercial_neighborhood: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    description: Mapped[Optional[str]] = mapped_column(Text)

    broker_properties: Mapped[list["BrokerProperty"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="select",
    )

    photos: Mapped[list["Photo"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="select",
        primaryjoin="Photo.ref == DBProperty.ref",
        uselist=True,
    )


class Broker(Base):
    __tablename__ = "brokers"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    cod: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    ddd: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    second_ddd: Mapped[Optional[str]] = mapped_column(Text)
    second_phone: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    second_email: Mapped[Optional[str]] = mapped_column(Text)
    third_email: Mapped[Optional[str]] = mapped_column(Text)
    team_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), server_default=func.gen_random_uuid()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    password: Mapped[Optional[str]] = mapped_column(Text)

    role: Mapped[list["BrokerRole"]] = relationship(
        "BrokerRole", lazy="select", uselist=False
    )

    properties: Mapped[list["BrokerProperty"]] = relationship(
        "BrokerProperty", back_populates="broker", lazy="select"
    )


class UserInterest(Base):
    __tablename__ = "user_interests"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'property'::text")
    )
    reference: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
