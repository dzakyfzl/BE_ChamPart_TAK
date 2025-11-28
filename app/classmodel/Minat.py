from pydantic import BaseModel
from typing import List

class JSONMinatRequest(BaseModel):
    minat_id: List[int]

class JSONMinat (BaseModel):
    idMinat: int
    nama_minat: str
