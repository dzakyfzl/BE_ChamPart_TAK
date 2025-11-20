from fastapi import APIRouter, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import and_, insert, select, delete, update

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token
from ..security.adminPass import generate_pass

router = APIRouter(
    prefix="/approve",
    tags=["Approval"]
)

@router.post('/instansi/baru',status_code=200)
def approve_pendaftaran_instansi(request: JSONApproveInstansi,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    
    query = None
    try:
        query = db.execute(select(CalonInstansi.nama,CalonInstansi.jenis,CalonInstansi.alamat,CalonInstansi.email_pengaju).select_from(CalonInstansi).where(and_(CalonInstansi.idCalonInstansi==request.idCalonInstansi,CalonInstansi.jenis_calon=="baru"))).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"instansi tidak ada pada daftar calon"}
    
    message = {"message":f"Instansi {query[0]} berhasil di approve"}
    if request.isApproved:
        try:
            db.execute(insert(Instansi).values(nama=query[0],jenis=query[1],alamat=query[2]))
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
    else:
        message = {"message":f"Instansi {query[0]} berhasil di reject"}
        
    try:
        db.execute(delete(CalonInstansi).where(CalonInstansi.idCalonInstansi==request.idCalonInstansi))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    try:
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return message

@router.post('/instansi/edit',status_code=200)
def approve_pendaftaran_instansi(request: JSONApproveInstansi,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    
    query = None
    try:
        query = db.execute(select(CalonInstansi.nama,CalonInstansi.jenis,CalonInstansi.alamat,CalonInstansi.email_pengaju).select_from(CalonInstansi).where(and_(CalonInstansi.idCalonInstansi==request.idCalonInstansi,CalonInstansi.jenis_calon=="edit"))).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"instansi tidak ada pada daftar edit"}
    
    message = {"message":f"Pengajuan edit Instansi {query[0]} berhasil di approve"}
    if request.isApproved:
        try:
            query2 = db.execute(select(AdminInstansi.idInstansi).where(AdminInstansi.email==query[3])).first()
            db.execute(update(Instansi).where(Instansi.idInstansi==query2[0]).values(nama=query[0],jenis=query[1],alamat=query[2]))
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
    else:
        message = {"message":f"Pengajuan edit Instansi {query[0]} berhasil di reject"}
        
    try:
        db.execute(delete(CalonInstansi).where(CalonInstansi.idCalonInstansi==request.idCalonInstansi))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    try:
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return message

@router.post('/admin-instansi',status_code=200)
def approve_pendaftaran_instansi(request: JSONApproveAdmin,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):

    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    query = None
    try:
        query = db.execute(select(Instansi.nama).select_from(Instansi).where(Instansi.idInstansi==request.idInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"instansi tidak ada/belum terdaftar"}
    
    message = {"message":f"sukses reject {request.email} dari instansi {query[0]}","passkey":"None"}
    if request.isApproved:
        hashed_passkey = generate_pass(request.unique_character,request.email,query[0])

        try:
            db.execute(insert(Passkey).values(isiPasskey=hashed_passkey,idInstansi=request.idInstansi))
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
        message = {"message":f"sukses mengapprove {request.email} dari instansi {query[0]}","passkey":request.unique_character}

    return message