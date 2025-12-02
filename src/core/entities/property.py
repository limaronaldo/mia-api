from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Property(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    active: bool = True
    ref: Optional[str]
    agency_code: Optional[str]
    property_type_code: Optional[int]
    property_type: Optional[str]
    business_type_code: Optional[str]
    use_type_code: Optional[str]
    origin_type_code: Optional[int]
    is_launch: Optional[int]
    zip_code: Optional[str]
    street_name: Optional[str]
    address: Optional[str]
    number: Optional[str]
    sql_id: Optional[str]
    location: Optional[Any] = None
    reference: Optional[str]
    city_code: Optional[int]
    city: Optional[str]
    state: Optional[str]
    region: Optional[str]
    neighborhood: Optional[str]
    neighborhood_code: Optional[int]
    region_code1: Optional[str]
    region_code2: Optional[str]
    region_code3: Optional[str]
    value: Optional[float]
    is_for_sale: Optional[int]
    sale_value: Optional[float]
    sale_value_per_m2: Optional[float]
    is_for_rent: Optional[int]
    rent_value: Optional[float]
    rent_value_per_m2: Optional[float]
    condo_fee: Optional[float]
    iptu: Optional[float]
    bedrooms: Optional[int]
    suites: Optional[int]
    parking_spaces: Optional[int]
    total_area: Optional[int]
    usable_area: Optional[int]
    size: Optional[str]
    promotion: Optional[str]
    unit_details: Optional[str]
    condo_details: Optional[str]
    tag: Optional[str]
    with_photos: Optional[int]
    with_text: Optional[int]
    with_financing: Optional[int]
    entry_value: Optional[float]
    installment_value: Optional[float]
    status: Optional[int]
    living_rooms: Optional[int]
    professional_code: Optional[str]
    development: Optional[str]
    complement: Optional[str]
    video: Optional[str]
    payment_conditions: Optional[str]
    surroundings: Optional[str]
    classification_code: Optional[int]
    bathrooms: Optional[int]
    exclusivity: Optional[int]
    on_call: Optional[int]
    remaining: Optional[int]
    accepts_swap: Optional[int]
    has_income: Optional[int]
    building_name: Optional[str]
    title: Optional[str]
    new_title: Optional[str]
    print_text: Optional[str]
    publication_date: Optional[datetime]
    publication_agency_code: Optional[str]
    photo_quantity: Optional[int]
    iptu_type: Optional[str]
    system_rule: Optional[str]
    photo_change_date: Optional[datetime]
    property_status: Optional[str]
    registration_date: Optional[datetime]
    available_for_seasonal_rental: Optional[int]
    seasonal_rental_value: Optional[float]
    capacity: Optional[int]
    disabled_property: Optional[int]
    rental_period: Optional[str]
    furniture_status: Optional[str]
    unit_features: Optional[str]
    condo_features: Optional[str]
    previous_code: Optional[str]
    development_photo_change_date: Optional[str | datetime]
    residential: Optional[str]
    commercial: Optional[str]
    rural: Optional[str]
    industrial: Optional[str]
    simplified_type_code: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        json_encoders = {UUID: lambda v: str(v)}
        from_attributes = True

    # def model_dump(self, *args, **kwargs):
    #     d = super().model_dump(*args, **kwargs)
    #     for k, v in d.items():
    #         if isinstance(v, datetime):
    #             d[k] = v.isoformat()
    #     return d
