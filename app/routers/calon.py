from fastapi import APIRouter, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import and_, insert, select, delete, update

from app.database.models.calonAdminInstansi import CalonAdminInstansi

from ..database.database import get_db

from ..database.models import *
from ..classmodel import *

from ..depedency import validate_token
from ..security.adminPass import generate_pass

router = APIRouter(
    prefix="/calon",
    tags=["Calon"]
)

@router.get("/admin-instansi/get")
def ambil_calon_admin_instansi(response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    data=[]
    query=None
    try:
        stmt=select(CalonAdminInstansi.idCalonAdminInstansi,CalonAdminInstansi.email,CalonAdminInstansi.idInstansi)
        query = db.execute(stmt).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        return {"message":"data calon admin instansi kosong"}
    
    for q in query:
        data.append({"idCalonAdminInstansi":q[0],"email":q[1],"idInstansi":q[2]})

    return {"message":"data calon admin instansi ditemukan","data":data}

@router.get("/instansi/baru/get")
def ambil_calon_instansi_baru(response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    data=[]
    query=None
    try:
        query=db.execute(select(CalonInstansi.idCalonInstansi,CalonInstansi.email_pengaju,CalonInstansi.nama,CalonInstansi.jenis,CalonInstansi.alamat).where(CalonInstansi.jenis_calon=="baru")).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        return {"message":"data calon instansi kosong"}
    
    for q in query:
        data.append({"idCalonInstansi":q[0],"email":q[1],"nama":q[2],"jenis":q[3],"alamat":q[4]})

    return {"message":"data calon instansi ditemukan","data":data}
    
@router.get("/instansi/edit/get")
def ambil_calon_instansi_edit(response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    data=[]
    query=None
    try:
        query=db.execute(select(CalonInstansi.idCalonInstansi,CalonInstansi.email_pengaju,CalonInstansi.nama,CalonInstansi.jenis,CalonInstansi.alamat).where(CalonInstansi.jenis_calon=="edit")).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        return {"message":"data calon instansi kosong"}
    
    for q in query:
        data.append({"idCalonInstansi":q[0],"email":q[1],"nama":q[2],"jenis":q[3],"alamat":q[4]})

    return {"message":"data calon instansi ditemukan","data":data}
