from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class CalonAdminInstansi(Base):
    __tablename__ = "CalonAdminInstansi"

    idCalonAdminInstansi = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)
    idInstansi = Column(Integer, ForeignKey('Instansi.idInstansi'), nullable=False)
    
    instansi = relationship("Instansi", backref="CalonAdminInstansi")
    
    def __repr__(self):
        return f"<AdminInstansi(idAdminInstansi={self.idCalonAdminInstansi}, email='{self.email}')>"
