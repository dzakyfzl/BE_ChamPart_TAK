from pydantic import BaseModel
from typing import List

class JSONBakatRequest(BaseModel):
    bakat_id: List[int]

class JSONBakat (BaseModel):
    idBakat: int
    nama_bakat: str