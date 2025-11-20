from pydantic import BaseModel

class JSONAccount(BaseModel):
    username: str
    email: str
    password: str

class JSONLogin(BaseModel):
    username: str
    password: str
    role: str

class JSONUpdatePassword(BaseModel):
    password_lama: str
    password_baru: str
