from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ToEnrichCustomers(Base):
    __tablename__ = "to_enrich_customers"
    __table_args__ = {"schema": "views"}

    id: Mapped[UUID] = mapped_column(primary_key=True)
    cpf: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"<ToEnrichCustomers(id={self.id}, cpf={self.cpf})>"
