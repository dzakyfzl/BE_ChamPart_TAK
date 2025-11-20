from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class AdminInstansi(Base):
    __tablename__ = "AdminInstansi"

    idAdminInstansi = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    jabatan = Column(String(100), nullable=False)
    salt = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    idInstansi = Column(Integer, ForeignKey('Instansi.idInstansi'), nullable=False)
    idLampiran = Column(Integer, ForeignKey('Lampiran.idLampiran'), nullable=True)
    
    instansi = relationship("Instansi", backref="AdminInstansi")
    lampiran = relationship("Lampiran", backref="AdminInstansi")
    
    def __repr__(self):
        return f"<AdminInstansi(idAdminInstansi={self.idAdminInstansi}, username='{self.username}')>"