from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .Minat import JSONMinat
from .Bakat import JSONBakat
from .Lampiran import JSONLampiran

class KegiatanBase(BaseModel):
    nama: str
    deskripsi: str
    waktu: datetime
    nominal_TAK: int
    TAK_wajib: bool
    idInstansi: int
    idLampiran: int

class JSONKegiatanCard(BaseModel):
    idKegiatan: int
    nama: str
    nama_instansi: str
    TAK_wajib: bool
    waktu: datetime
    waktuDiupload: datetime
    views: int
    minat: List[JSONMinat] = []
    bakat: List[JSONBakat] = []


    class Config:
        orm_mode = True


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

class JSONChangeStatus(BaseModel):
    status: str


class JSONKegiatanDetail(BaseModel):
    idKegiatan: int
    nama: str
    deskripsi: str
    waktu: datetime
    nominal_TAK: int
    TAK_wajib: bool
    status_kegiatan: str
    waktuDiupload: datetime
    views: int
    nama_instansi: str
    lampiran: Optional[JSONLampiran] = None
    minat: List[JSONMinat] = []
    bakat: List[JSONBakat] = []

    class Config:
        from_attributes = True