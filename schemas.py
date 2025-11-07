from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Verify2FA(BaseModel):
    email: str
    code: str