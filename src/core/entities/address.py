from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Address(BaseModel):
    street: Optional[str] = Field(None, description="Street name")
    number: Optional[str] = Field(None, description="Street number")
    neighborhood: Optional[str] = Field(None, description="Neighborhood name")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State name")
    cep: Optional[str] = Field(None, description="Postal code")
    customer_id: Optional[int] = Field(
        None, description="Customer identifier associated with the address"
    )
    company_id: Optional[int] = Field(
        None, description="Company identifier associated with the address"
    )
    created_at: Optional[datetime] = Field(
        description="Timestamp of when the address was created",
        default=datetime.now().isoformat(),
    )
    updated_at: Optional[datetime] = Field(
        description="Timestamp of when the address was last updated",
        default=datetime.now().isoformat(),
    )
    complement: Optional[str] = Field(
        None, description="Additional address details or complement"
    )
    ranking: Optional[int] = Field(None, description="Address ranking or priority")
    latitude: Optional[float] = Field(
        None, description="Latitude coordinate of the address location"
    )
    longitude: Optional[float] = Field(
        None, description="Longitude coordinate of the address location"
    )
    ddd: Optional[int] = Field(None, description="Area code for the address location")
    street_type: Optional[str] = Field(
        None, description="Type of street (e.g., Avenue, Street, Boulevard)"
    )
    full_street: Optional[str] = Field(
        None, description="Full street name including type and number"
    )
    state_ibge_code: Optional[str] = Field(None, description="IBGE code for the state")
    city_ibge_code: Optional[str] = Field(None, description="IBGE code for the city")
