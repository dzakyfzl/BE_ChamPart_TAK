from pydantic import BaseModel

class JSONApproveInstansi(BaseModel):
    idCalonInstansi: int
    isApproved: bool

class JSONApproveAdmin(BaseModel):
    email: str
    unique_character: str
    idInstansi: int
    isApproved: bool

class JSONApproveAdminPengawas(BaseModel):
    email: str
    unique_character: str