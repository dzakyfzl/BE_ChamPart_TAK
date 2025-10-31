from sqlalchemy import Column, Integer, String
from app.database.database import Base
from .minatPengguna import minatPengguna

class Minat(Base):
    __tablename__ = "Minat"
    
    idMinat = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    
    def __repr__(self):
        return f"<Minat(idMinat={self.idMinat}, nama='{self.nama}')>"