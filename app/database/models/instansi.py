from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Instansi(Base):
    __tablename__ = "Instansi"

    idInstansi = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    jenis = Column(String(50), nullable=False)
    alamat = Column(String(255), nullable=False)
    idLampiran = Column(Integer, ForeignKey('lampiran.idLampiran'), nullable=False)

    lampiran = relationship("Lampiran", backref="instansi")
    
    def __repr__(self):
        return f"<Instansi(idInstansi={self.idInstansi}, nama={self.nama})>"