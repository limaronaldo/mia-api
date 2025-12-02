from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Company(BaseModel):
    cnpj: Optional[str] = Field(None, description="Company CNPJ")
    legal_name: Optional[str] = Field(None, description="Company legal name")
    fantasy_name: Optional[str] = Field(None, description="Company fantasy name")
    activity_code: Optional[str] = Field(None, description="Company activity code")
    activity_description: Optional[str] = Field(
        None, description="Company activity description"
    )
    registration_status: Optional[str] = Field(
        None, description="Company registration status"
    )
    legal_nature: Optional[str] = Field(None, description="Company legal nature")
    nature: Optional[str] = Field(None, description="Company nature")
    created_at: Optional[datetime] = Field(
        description="Timestamp of when the company record was created",
        default=datetime.now().isoformat(),
    )
    opening_date: Optional[str] = Field(None, description="Company opening date")
    employees_range: Optional[str] = Field(None, description="Company employees range")
    legal_type: Optional[str] = Field(None, description="Company legal type")
    type: Optional[str] = Field(None, description="Company type")
    size: Optional[str] = Field(None, description="Company size")
    registration_status_reason: Optional[str] = Field(
        None, description="Company registration status reason"
    )
    special_status_reason: Optional[str] = Field(
        None, description="Company special status reason"
    )
    registration_status_date: Optional[str] = Field(
        None, description="Company registration status date"
    )
    special_status_date: Optional[str] = Field(
        None, description="Company special status date"
    )

    @field_validator("opening_date")
    @classmethod
    def parse_opening_date(cls, value):
        if value is not None:
            day, month, year = value.split("/")
            return "{year}-{month}-{day}".format(year=year, month=month, day=day)
        return value
