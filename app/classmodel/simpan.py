from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class JSONSimpanRequest(BaseModel):
    idKegiatan: int

class JSONSimpanResponse(BaseModel):
    idKegiatan: int
    nama_kegiatan: str
    deskripsi: str
    waktu_kegiatan: datetime
    nominal_TAK: int
    TAK_wajib: bool
    status_kegiatan: str
    nama_instansi: str
    waktu_disimpan: datetime

class JSONSimpanList(BaseModel):
    total: int
    kegiatan: List[JSONSimpanResponse]