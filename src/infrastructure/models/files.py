import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.config.database import Base

if TYPE_CHECKING:
    from .public import Iptu


class IptuFile(Base):
    __tablename__ = "iptu"
    __table_args__ = {"schema": "files"}

    instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        nullable=False,
    )
    exercise_year: Mapped[int] = mapped_column(Integer, nullable=False)
    contributor_number: Mapped[str] = mapped_column(
        ForeignKey("public.iptus.contributor_number"), nullable=False
    )
    s3_uri: Mapped[str] = mapped_column(Text, nullable=True)
    object_uri: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
        nullable=False,
    )

    iptu: Mapped["Iptu"] = relationship(
        "Iptu",
        back_populates="files",
        lazy="select",
        primaryjoin="IptuFile.contributor_number == Iptu.contributor_number",
    )
