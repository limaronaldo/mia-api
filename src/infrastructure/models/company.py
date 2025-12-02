from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=UUID)
    cnpj: Mapped[str] = mapped_column(nullable=True)
    legal_name: Mapped[str] = mapped_column(nullable=True)
    fantasy_name: Mapped[str] = mapped_column(nullable=True)
    opening_date: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)
    size: Mapped[str] = mapped_column(nullable=True)
    registration_status_date: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
