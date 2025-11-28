from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base

class Simpan(Base):
    __tablename__ = 'Simpan'
    
    idPengguna = Column(Integer, ForeignKey('Pengguna.idPengguna'), primary_key=True)
    idKegiatan = Column(Integer, ForeignKey('Kegiatan.idKegiatan'), primary_key=True)
    waktu = Column(DateTime, nullable=False)
    
    pengguna = relationship("Pengguna", back_populates="simpan_kegiatan")
    kegiatan = relationship("Kegiatan", back_populates="disimpan_oleh")