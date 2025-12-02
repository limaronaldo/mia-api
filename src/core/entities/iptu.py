from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.infrastructure.models.company import Company
from src.infrastructure.models.customer import Customer


class Iptu(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    contributor_number: Optional[str]
    exercise_year: Optional[int]
    nl_number: Optional[int]
    registration_date: Optional[datetime]
    condominium_number: Optional[str]
    property_codlog: Optional[str]
    property_street_name: Optional[str]
    property_number: Optional[float]
    property_complement: Optional[str]
    property_neighborhood: Optional[str]
    property_reference: Optional[str]
    property_postal_code: Optional[str]
    corners_fronts_quantity: Optional[int]
    ideal_fraction: Optional[float]
    land_area: Optional[float]
    built_area: Optional[float]
    occupied_area: Optional[float]
    land_m2_value: Optional[float]
    construction_m2_value: Optional[float]
    corrected_construction_year: Optional[int]
    floors_quantity: Optional[int]
    calculation_frontage: Optional[float]
    property_usage_type: Optional[str]
    construction_standard_type: Optional[str]
    land_type: Optional[str]
    obsolescence_factor: Optional[float]
    contributor_life_start_year: Optional[int]
    contributor_life_start_month: Optional[int]
    contributor_phase: Optional[int]
    company: Optional[Company]
    customer: Optional[Customer]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
