from sqlalchemy import Column, Integer, String
from app.database.database import Base

class Lampiran(Base):
    __tablename__ = "Lampiran"

    idLampiran = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(50), nullable=False)
    ukuran = Column(Integer, nullable=False)
    folder = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Lampiran(idLampiran={self.idLampiran}, nama='{self.nama}')>"