from .Account import JSONAccount, JSONLogin
from .AdminPengawas import JSONAdminPengawas
from .AdminInstansi import JSONAdminInstansi, JSONCalonInstansi
from .Pengguna import JSONPengguna
from .Minat import JSONMinatRequest
from .Bakat import JSONBakatRequest
from .Approve import JSONApproveInstansi, JSONApproveAdmin
from .Kegiatan import (
    JSONKegiatanCreate,
    JSONKegiatanUpdate,
    JSONKegiatanResponse,
    JSONKegiatanDetail
)

__all__ = [
    "JSONAccount",
    "JSONLogin",
    "JSONPengguna",
    "JSONAdminInstansi",
    "JSONCalonInstansi",
    "JSONAdminPengawas",
    "JSONApproveInstansi",
    "JSONApproveAdmin",
    "JSONKegiatanCreate",
    "JSONKegiatanUpdate",
    "JSONKegiatanResponse",
    "JSONKegiatanDetail",
    "JSONMinatRequest",
    "JSONBakatRequest"
]