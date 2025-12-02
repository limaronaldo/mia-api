from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Email(BaseModel):
    email: EmailStr = Field(None, description="The email address.")
    created_at: Optional[datetime] = Field(
        description="The timestamp when the email was created.",
        default=datetime.now().isoformat(),
    )
    updated_at: Optional[datetime] = Field(
        description="The timestamp when the email was last updated.",
        default=datetime.now().isoformat(),
    )
    customer_id: int = Field(
        None,
        description="The unique identifier for the customer associated with the email.",
    )
    company_id: Optional[int] = Field(
        None,
        description="The unique identifier for the company associated with the email, if applicable.",
    )
    ranking: Optional[int] = Field(
        None, description="The ranking or priority of the email, if applicable."
    )
