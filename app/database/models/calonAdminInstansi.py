from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base

class CalonAdminInstansi(Base):
    __tablename__ = "CalonAdminInstansi"
    idAdmin = Column(Integer, primary_key=True, autoincrement=True)
    idInstansi = Column(Integer, ForeignKey("Instansi.idInstansi"))
    email = Column(String, nullable=False)
    email_pengaju = Column(String, nullable=False)