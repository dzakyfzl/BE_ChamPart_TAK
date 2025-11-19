from pydantic import BaseModel

class JSONAccount(BaseModel):
    nama: str
    email: str
    password: str

class JSONLogin(BaseModel):
    email: str
    password: str
    role: str
