from sqlalchemy import Column, Integer, String, Text
from app.database.database import Base

class RefreshToken(Base):
    __tablename__ = "RefreshToken"

    idRefreshToken = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    isi = Column(Text, nullable=False)
    


    def __repr__(self):
        return f"<RefreshToken(idRefreshToken={self.idRefreshToken}, username='{self.username}', isi='{self.isi}')>"
