from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Pengguna(Base):
    __tablename__ = "Pengguna"

    idPengguna = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    no_telp = Column(String(15), nullable=False)
    prodi = Column(String(100), nullable=False)
    salt = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    idLampiran = Column(Integer, ForeignKey('lampiran.idLampiran'), nullable=False)
  
    lampiran = relationship("Lampiran", backref="pengguna")

    def __repr__(self):
        return f"<Pengguna(idPengguna={self.idPengguna}, nama='{self.nama}')>"
