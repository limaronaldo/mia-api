from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Phone(BaseModel):
    created_at: Optional[datetime] = Field(
        description="The timestamp when the phone record was created.",
        default=datetime.now().isoformat(),
    )
    updated_at: Optional[datetime] = Field(
        description="The timestamp when the phone record was last updated.",
        default=datetime.now().isoformat(),
    )
    ddd: str = Field(
        None, description="The area code for the phone number.", max_length=2
    )
    phone: str = Field(..., description="The phone number without the area code.")
    operator: Optional[str] = Field(
        None, description="The name of the phone operator or service provider."
    )
    type: Optional[str] = Field(
        None,
        description="The type or category of the phone number (e.g., mobile, landline).",
    )
    ranking: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="A ranking or score associated with the phone number.",
    )
