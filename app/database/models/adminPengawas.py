from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class AdminPengawas(Base):
    __tablename__ = "AdminPengawas"
    
    idAdminPengawas = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    jabatan = Column(String(100), nullable=False)
    salt = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    idLampiran = Column(Integer, ForeignKey('lampiran.idLampiran'), nullable=False)
    
    lampiran = relationship("Lampiran", backref="admin_pengawas")
    
    def __repr__(self):
        return f"<AdminPengawas(idAdminPengawas={self.idAdminPengawas}, nama='{self.nama}')>"