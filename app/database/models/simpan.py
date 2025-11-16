from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from app.database.database import Base

simpan = Table(
    'Simpan',
    Base.metadata,
    Column('idPengguna', Integer, ForeignKey('Pengguna.idPengguna'), primary_key=True),
    Column('idKegiatan', Integer, ForeignKey('kegiatan.idKegiatan'), primary_key=True),
    Column('waktu', DateTime, nullable=False)
)