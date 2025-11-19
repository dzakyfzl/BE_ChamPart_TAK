from pydantic import BaseModel
from .Account import JSONAccount

class JSONAdminInstansi(JSONAccount):
    jabatan: str
    idInstansi: int
    passkey:str

class JSONCalonInstansi(BaseModel):
    nama: str
    jenis: str
    alamat: str
    email_pengaju: str