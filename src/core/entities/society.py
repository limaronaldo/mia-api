from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Society(BaseModel):
    cpf: Optional[str] = Field(
        None,
        description="The CPF (Brazilian individual registry identification) of the society member.",
    )
    name: Optional[str] = Field(None, description="The name of the society member.")
    role: Optional[str] = Field(
        None,
        description="The role or position of the society member within the organization.",
    )
    participation: Optional[str] = Field(
        None, description="The level or type of participation of the society member."
    )
    entry_date: Optional[str] = Field(
        None, description="The date when the society member joined or became a member."
    )
    has_restriction: Optional[str] = Field(
        None,
        description="Indicates whether the society member has any restrictions or limitations.",
    )
    created_at: Optional[datetime] = Field(
        description="The timestamp when the society member record was created.",
        default=datetime.now().isoformat(),
    )
    updated_at: Optional[datetime] = Field(
        description="The timestamp when the society member record was last updated.",
        default=datetime.now().isoformat(),
    )
    company_id: Optional[int] = Field(
        None,
        description="The unique identifier of the company or organization the society member belongs to.",
    )
