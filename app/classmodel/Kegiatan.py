from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class KegiatanBase(BaseModel):
    nama: str
    deskripsi: str
    waktu: datetime
    nominal_TAK: int
    TAK_wajib: bool
    status_kegiatan: str
    idAdminPengawas: int
    idAdminInstansi: int
    idInstansi: int
    idLampiran: int

class JSONKegiatanCreate(KegiatanBase):
    minat_id: List[int] = []
    bakat_id: List[int] = []

class JSONKegiatanUpdate(BaseModel):
    nama: Optional[str] = None
    deskripsi: Optional[str] = None
    waktu: Optional[datetime] = None
    nominal_TAK: Optional[int] = None
    TAK_wajib: Optional[bool] = None
    status_kegiatan: Optional[str] = None
    idAdminPengawas: Optional[int] = None
    idAdminInstansi: Optional[int] = None
    idInstansi: Optional[int] = None
    idLampiran: Optional[int] = None
    minat_id: Optional[List[int]] = None
    bakat_id: Optional[List[int]] = None

class JSONKegiatanResponse(KegiatanBase):
    idKegiatan: int
    waktuDiupload: datetime

    class Config:
        orm_mode = True

class JSONKegiatanDetail(JSONKegiatanResponse):
    minat_list: List[dict] = []  
    bakat_list: List[dict] = []  
    
    class Config:
        orm_mode = True