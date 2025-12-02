from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional


class IptuFile(BaseModel):
    instance_id: UUID
    exercise_year: int
    contributor_number: str
    s3_uri: Optional[str] = None
    object_uri: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    id: UUID = Field(default_factory=uuid4)

    class Config:
        from_attributes = True


class IptuContributor(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    contributor_number: str
    customer_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    exercise_year: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class Broker(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    cod: Optional[str] = None
    name: str
    ddd: Optional[str] = None
    phone: Optional[str] = None
    second_ddd: Optional[str] = None
    second_phone: Optional[str] = None
    email: str
    second_email: Optional[str] = None
    third_email: Optional[str] = None
    team_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True
