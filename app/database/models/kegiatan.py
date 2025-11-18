from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from .minatKegiatan import minatKegiatan
from .bakatKegiatan import bakatKegiatan

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
    
    admin_pengawas = relationship("AdminPengawas", backref="kegiatan")
    admin_instansi = relationship("AdminInstansi", backref="kegiatan")
    instansi = relationship("Instansi", backref="kegiatan")
    lampiran = relationship("Lampiran", backref="kegiatan")
    minat_list = relationship("Minat", secondary=minatKegiatan, backref="kegiatan_list")
    bakat_list = relationship("Bakat", secondary=bakatKegiatan, backref="kegiatan_list")

    def __repr__(self):
        return f"<Kegiatan(idKegiatan={self.idKegiatan}, nama='{self.nama}')>"