from sqlalchemy import Column, Integer, String, Float

from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    budget_limit = Column(Float, nullable=True)
    icon = Column(String)
    color = Column(String)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, icon={self.icon})>"
