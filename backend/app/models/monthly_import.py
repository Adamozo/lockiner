from sqlalchemy import Column, Integer, String

from .base import Base, utc_now


class MonthlyImport(Base):
    __tablename__ = "monthly_imports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    month = Column(String, nullable=False, index=True)  # YYYY-MM format
    filename = Column(String)
    transactions_count = Column(Integer)
    imported_at = Column(String, default=lambda: utc_now().isoformat())

    def __repr__(self):
        return f"<MonthlyImport(id={self.id}, month={self.month}, count={self.transactions_count})>"
