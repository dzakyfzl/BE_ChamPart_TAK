from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from .minatPengguna import minatPengguna
from .bakatPengguna import bakatPengguna
from .simpan import simpan

class Pengguna(Base):
    __tablename__ = "Pengguna"

    idPengguna = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    no_telp = Column(String(15), nullable=False)
    fakultas = Column(String(100), nullable=False)
    prodi = Column(String(100), nullable=False)
    salt = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    idLampiran = Column(Integer, ForeignKey('Lampiran.idLampiran'), nullable=True)
  
    lampiran = relationship("Lampiran", backref="pengguna")
    minat_list = relationship("Minat", secondary=minatPengguna, backref="pengguna_list")
    bakat_list = relationship("Bakat", secondary=bakatPengguna, backref="pengguna_list")
    kegiatan_simpan = relationship("Kegiatan", secondary=simpan, backref="pengguna_simpan")


    def __repr__(self):
        return f"<Pengguna(idPengguna={self.idPengguna}, nama='{self.nama}')>"
