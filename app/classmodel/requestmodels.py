from pydantic import BaseModel

class JSONAccount(BaseModel):
    nama: str
    email: str
    password: str

class JSONLogin(BaseModel):
    email: str
    password: str
    role: str

class JSONPengguna(JSONAccount):
    no_telp: str
    prodi: str
    fakultas: str

class JSONAdminInstansi(JSONAccount):
    jabatan: str
    idInstansi: int
    passkey:str

class JSONAdminPengawas(JSONAccount):
    jabatan: str

class JSONCalonInstansi(BaseModel):
    nama: str
    jenis: str
    alamat: str
    email_pengaju: str

class JSONMinatBakat(BaseModel):
    minat: list[int]
    bakat: list[int]

class JSONApproveInstansi(BaseModel):
    idCalonInstansi: int
    isApproved: bool

class JSONApproveAdmin(BaseModel):
    email: str
    unique_character: str
    idInstansi: int
    isApproved: bool

    