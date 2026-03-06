from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, utc_now


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(String(100), unique=True, nullable=False, index=True)
    client_name = Column(String(100), nullable=False)
    redirect_uris = Column(Text, nullable=False)  # JSON array jako string
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    authorization_codes = relationship("OAuthAuthorizationCode", back_populates="client", cascade="all, delete-orphan")
    access_tokens = relationship("OAuthAccessToken", back_populates="client", cascade="all, delete-orphan")


class OAuthAuthorizationCode(Base):
    __tablename__ = "oauth_authorization_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(128), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("oauth_clients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code_challenge = Column(String(128), nullable=False)
    code_challenge_method = Column(String(10), nullable=False, default="S256")
    redirect_uri = Column(String(500), nullable=False)
    expires_at = Column(String, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    client = relationship("OAuthClient", back_populates="authorization_codes")
    user = relationship("User")


class OAuthAccessToken(Base):
    __tablename__ = "oauth_access_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    access_token = Column(String(256), unique=True, nullable=False, index=True)
    refresh_token = Column(String(256), unique=True, nullable=True, index=True)
    client_id = Column(Integer, ForeignKey("oauth_clients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(String, nullable=False)
    refresh_token_expires_at = Column(String, nullable=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    client = relationship("OAuthClient", back_populates="access_tokens")
    user = relationship("User")


class OAuthDeviceCode(Base):
    __tablename__ = "oauth_device_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_code = Column(String(256), unique=True, nullable=False, index=True)
    user_code = Column(String(20), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("oauth_clients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending/approved/denied
    expires_at = Column(String, nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    client = relationship("OAuthClient")
    user = relationship("User")
