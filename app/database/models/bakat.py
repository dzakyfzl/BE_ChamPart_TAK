from sqlalchemy import Column, Integer, String
from app.database.database import Base

class Bakat(Base):
    __tablename__ = "Bakat"
    
    idBakat = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    
    def __repr__(self):
        return f"<Bakat(idBakat={self.idBakat}, nama='{self.nama}')>"