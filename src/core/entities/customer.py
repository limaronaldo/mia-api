from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Customer(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = Field(None, description="Name of the customer")
    sex: Optional[str] = Field(None, description="Gender of the customer")
    birth_date: Optional[datetime] = Field(
        None, description="Date of birth of the customer"
    )
    cpf: Optional[str] = Field(
        None,
        description="Brazilian CPF (Individual Taxpayer Registry) number of the customer",
    )
    mother_name: Optional[str] = Field(
        None, description="Name of the customer's mother"
    )
    father_name: Optional[str] = Field(
        None, description="Name of the customer's father"
    )
    created_at: Optional[datetime] = Field(
        description="Timestamp of when the customer record was created",
        default=datetime.now().isoformat(),
    )
    updated_at: Optional[datetime] = Field(
        description="Timestamp of when the customer record was last updated",
        default=datetime.now().isoformat(),
    )
