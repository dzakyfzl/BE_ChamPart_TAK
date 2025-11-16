from sqlalchemy import Column, Integer, String
from app.database.database import Base

class CalonInstansi(Base):
    __tablename__ = "CalonInstansi"

    idCalonInstansi = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    jenis = Column(String(50), nullable=False)
    alamat = Column(String(255), nullable=False)
    email_pengaju = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<CalonInstansi(idCalonInstansi={self.idCalonInstansi}, nama={self.nama})>"