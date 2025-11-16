from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

bakatPengguna = Table(
    'bakatPengguna',
    Base.metadata,
        Column('idBakat', Integer, ForeignKey('Bakat.idBakat'), primary_key=True),
        Column('idPengguna', Integer, ForeignKey('Pengguna.idPengguna'), primary_key=True)
)