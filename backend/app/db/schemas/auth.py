from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserPwChange(BaseModel):
    token: Token
    old_password: str
    new_password: str

class TokenWith2FA(Token):
    requires_2fa: bool = False
