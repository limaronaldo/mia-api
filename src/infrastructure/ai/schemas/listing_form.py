from typing import Literal, Optional

from pydantic import BaseModel, Field


class AdvertiseExpectedValue(BaseModel):
    min_expected_value: float = Field(default=0.0, ge=0.0)
    max_expected_value: float = Field(default=1000000.0, ge=0.0)


class ListingForm(BaseModel):
    advertise_type: Literal["sell", "rent"] = Field(default="sell")

    advertiser_name: str = Field(default="John Doe", max_length=100)
    advertiser_email: str = Field(default="john.doe@example.com", max_length=100)
    advertiser_phone: str = Field(default="123-456-7890", max_length=20)

    property_street_name: str = Field(default="Main Street", max_length=100)
    property_street_number: str = Field(default="123", max_length=10)
    property_neighborhood: str = Field(default="Downtown", max_length=100)
    property_city: str = Field(default="New York", max_length=100)

    property_bedrooms: int = Field(default=2, ge=0)
    property_bathrooms: int = Field(default=2, ge=0)
    property_area: float = Field(default=100.0, ge=0.0)

    property_extra_features: str | None = Field(default=None, max_length=500)

    advertise_expected_value: AdvertiseExpectedValue = Field(
        default=AdvertiseExpectedValue(min_budget=0.0, max_budget=1000000.0)
    )
    advertise_months_duration: Optional[int] = Field(default=None, ge=0)
