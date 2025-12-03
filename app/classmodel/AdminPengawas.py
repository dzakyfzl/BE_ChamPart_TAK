from .Account import JSONAccount
from pydantic import BaseModel

class JSONAdminPengawas(JSONAccount):
    jabatan: str
    passkey:str

class JSONaktivasiRegister(BaseModel):
    register_admin_pengawas: bool