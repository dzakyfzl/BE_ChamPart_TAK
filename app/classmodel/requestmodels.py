from pydantic import BaseModel

class JSONAccount(BaseModel):
    nama: str
    email: str
    password: str

class JSONPengguna(JSONAccount):
    no_telp: str
    prodi: str
    fakultas: str

class JSONAdminInstansi(JSONAccount):
    jabatan: str

class JSONAdminPengawas(JSONAccount):
    jabatan: str


    