from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

minatKegiatan = Table(
    'minatKegiatan',
    Base.metadata,
    Column('idMinat', Integer, ForeignKey('Minat.idMinat'), primary_key=True),
    Column('idKegiatan', Integer, ForeignKey('Kegiatan.idKegiatan'), primary_key=True)
)