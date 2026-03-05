from pydantic import BaseModel
from typing import Optional


class OAuthAuthorizeParams(BaseModel):
    client_id: str
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str = "S256"
    response_type: str = "code"
    state: Optional[str] = None


class OAuthTokenRequest(BaseModel):
    grant_type: str
    code: Optional[str] = None
    code_verifier: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: str


class OAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class OAuthUserInfoResponse(BaseModel):
    sub: str
    name: str
    email_hash: str
    role: str
