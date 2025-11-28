from pydantic import BaseModel

class JSONLampiran(BaseModel):
    idLampiran: int
    nama: str
    jenis: str
    ukuran: int
    folder: str