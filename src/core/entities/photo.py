from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime


class Photo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    ref: str
    seq: int
    title: Optional[str] = None
    src: dict
    featured: Optional[int] = None
    created_at: str = Field(default_factory=datetime.now)
    updated_at: Optional[str] = None
    metrics: Optional[dict] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
