from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

bakatKegiatan = Table(
    'bakatKegiatan',
    Base.metadata,
    Column('idBakat', Integer, ForeignKey('Bakat.idBakat'), primary_key=True),
    Column('idKegiatan', Integer, ForeignKey('Kegiatan.idKegiatan'), primary_key=True)
)