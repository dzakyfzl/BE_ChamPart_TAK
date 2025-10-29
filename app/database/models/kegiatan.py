from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Kegiatan(Base):
    __tablename__ = "kegiatan"

    idKegiatan = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    deskripsi = Column(Text, nullable=False)
    waktu = Column(DateTime, nullable=False)
    nominal_TAK = Column(Integer, nullable=False)
    TAK_wajib = Column(Boolean, nullable=False)
    status_kegiatan = Column(String(50), nullable=False)
    waktuDiupload = Column(DateTime, nullable=False)
    idAdminPengawas = Column(Integer, ForeignKey('adminpengawas.idAdminPengawas'), nullable=False)
    idAdminInstansi = Column(Integer, ForeignKey('admininstansi.idAdminInstansi'), nullable=False)
    idInstansi = Column(Integer, ForeignKey('instansi.idInstansi'), nullable=False)
    idLampiran = Column(Integer, ForeignKey('lampiran.idLampiran'), nullable=False)
    
    admin_pengawas = relationship("AdminPengawas", backref="kegiatan")
    admin_instansi = relationship("AdminInstansi", backref="kegiatan")
    instansi = relationship("Instansi", backref="kegiatan")
    lampiran = relationship("Lampiran", backref="kegiatan")
    
    def __repr__(self):
        return f"<Kegiatan(idKegiatan={self.idKegiatan}, nama='{self.nama}')>"