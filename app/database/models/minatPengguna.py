from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

minatPengguna = Table(
    'minatPengguna',
    Base.metadata,
    Column('idMinat', Integer, ForeignKey('minat.idMinat'), primary_key=True),
    Column('idPengguna', Integer, ForeignKey('pengguna.idPengguna'), primary_key=True)
)
    