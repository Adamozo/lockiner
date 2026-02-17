"""Journal Module Models."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class JournalEntry(Base):
    """Daily journal entry for a user."""
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_journal_entries_user_date"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    mood_score = Column(Integer, nullable=True)  # 1-10
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    items = relationship("JournalItem", back_populates="entry", cascade="all, delete-orphan", order_by="JournalItem.category, JournalItem.position")

    def __repr__(self):
        return f"<JournalEntry(id={self.id}, date={self.date}, mood={self.mood_score})>"


class JournalItem(Base):
    """Individual item within a journal entry."""
    __tablename__ = "journal_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False)  # accomplished|grateful|proud|annoyed|learned
    position = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    # Relationships
    entry = relationship("JournalEntry", back_populates="items")

    def __repr__(self):
        return f"<JournalItem(id={self.id}, category={self.category}, pos={self.position})>"


class JournalReport(Base):
    """Pre-computed journal report summary."""
    __tablename__ = "journal_reports"
    __table_args__ = (
        UniqueConstraint("user_id", "report_type", "period", name="uq_journal_reports_user_type_period"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_type = Column(String, nullable=False)  # monthly|yearly
    period = Column(String, nullable=False)  # YYYY-MM or YYYY
    data = Column(Text, nullable=False)  # JSON string
    entry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<JournalReport(id={self.id}, type={self.report_type}, period={self.period})>"
