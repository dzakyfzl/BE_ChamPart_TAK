from sqlalchemy import Column, Integer, ForeignKey, String
from app.database.database import Base
from sqlalchemy.orm import relationship

class Passkey(Base):
    __tablename__ = "Passkey"
    
    isiPasskey = Column(String(256), primary_key=True, nullable=False)
    idInstansi = Column(Integer,ForeignKey('Instansi.idInstansi'), nullable=False)

    instansi = relationship("Instansi", backref="passkey")

    
    def __repr__(self):
        return f"<Passkey(isiPasskey={self.isiPasskey}, idInstansi='{self.idInstansi}')>"