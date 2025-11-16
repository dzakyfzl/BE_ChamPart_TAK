from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

minatPengguna = Table(
    'minatPengguna',
    Base.metadata,
    Column('idMinat', Integer, ForeignKey('Minat.idMinat')),
    Column('idPengguna', Integer, ForeignKey('Pengguna.idPengguna'))
)
    