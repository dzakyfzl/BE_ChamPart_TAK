from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Kegiatan(Base):
    __tablename__ = "Kegiatan"

    idKegiatan = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    deskripsi = Column(Text, nullable=False)
    waktu = Column(DateTime, nullable=False)
    nominal_TAK = Column(Integer, nullable=False)
    TAK_wajib = Column(Boolean, nullable=False)
    status_kegiatan = Column(String(50), nullable=False)
    waktuDiupload = Column(DateTime, nullable=False)
    idAdminPengawas = Column(Integer, ForeignKey('AdminPengawas.idAdminPengawas'), nullable=False)
    idAdminInstansi = Column(Integer, ForeignKey('AdminInstansi.idAdminInstansi'), nullable=False)
    idInstansi = Column(Integer, ForeignKey('Instansi.idInstansi'), nullable=False)
    idLampiran = Column(Integer, ForeignKey('Lampiran.idLampiran'), nullable=False)
    
    admin_pengawas = relationship("AdminPengawas", backref="Kegiatan")
    admin_instansi = relationship("AdminInstansi", backref="Kegiatan")
    instansi = relationship("Instansi", backref="Kegiatan")
    lampiran = relationship("Lampiran", backref="Kegiatan")
    
    def __repr__(self):
        return f"<Kegiatan(idKegiatan={self.idKegiatan}, nama='{self.nama}')>"