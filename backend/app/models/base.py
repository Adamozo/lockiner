from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


def utc_now():
    return datetime.now(timezone.utc)
