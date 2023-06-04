from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str = ""
    expires: datetime = None


class TokenData(BaseModel):
    username: str | None = None
