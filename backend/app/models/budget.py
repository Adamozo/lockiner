from sqlalchemy import Column, Integer, Float, Boolean, String

from .base import Base, utc_now


class BudgetSettings(Base):
    __tablename__ = "budget_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    overall_monthly_limit = Column(Float, nullable=True)
    alert_threshold_warning = Column(Float, default=80.0)
    alert_threshold_danger = Column(Float, default=100.0)
    enable_alerts = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    def __repr__(self):
        return f"<BudgetSettings(id={self.id}, overall_limit={self.overall_monthly_limit}, alerts={self.enable_alerts})>"
