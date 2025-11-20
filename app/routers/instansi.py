from fastapi import APIRouter, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..auth.jwt_auth import create_token
from ..depedency import validate_token
from ..security.adminPass import verif_pass
from email_validator import validate_email, EmailNotValidError
import os
import hashlib

# register instansi
@router.post('/register/instansi',status_code=200)
def register_instansi(instansi :JSONCalonInstansi, response:Response, db:Session = Depends(get_db)):
    try:
        v = validate_email(instansi.email_pengaju)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    try:
        db.execute(insert(CalonInstansi).values(nama=instansi.nama,jenis=instansi.jenis,alamat=instansi.alamat,email_pengaju=instansi.email_pengaju))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":"instansi berhasil diajukan dan dalam proses verifikasi, cek email secara berkala"}

# edit instansi yang hanya bisa dilakukan oleh admin instansi yang bersangkutan
@router.put('/edit/instansi',status_code=200)
def edit_instansi(instansi: JSONEditInstansi, user: Annotated[dict, Depends(validate_token)], response:Response, db:Session = Depends(get_db)):
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    try:
        db.execute(
            text(
                "UPDATE instansi SET nama = :nama, jenis = :jenis, alamat = :alamat WHERE idInstansi = :idInstansi"
            ),
            {
                "nama": instansi.nama,
                "jenis": instansi.jenis,
                "alamat": instansi.alamat,
                "idInstansi": user["idInstansi"],
            },
        )
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":"data instansi berhasil diupdate"}

# edit instansi oleh admin instansi tapi masuk tabel ke calon instansi dan dia ngambil id dari admin instansi yang melakukan request
@router.put('/edit/instansi/admin',status_code=200)
def edit_instansi_by_admin(instansi: JSONEditInstansiByAdmin, user: Annotated[dict, Depends(validate_token)], response:Response, db:Session = Depends(get_db)):
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    try:
        db.execute(
            insert(CalonInstansi).values(
                idCalonInstansi = instansi.idCalonInstansi,
                nama = instansi.nama,
                jenis = instansi.jenis,
                alamat = instansi.alamat,
                email_pengaju = user["email"],
                status = "edit"
            )
        )
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":"data instansi berhasil diajukan untuk diupdate, menunggu verifikasi dari admin pengawas"}

# show all instansi
@router.get('instansi/showAll',status_code=200)
def show_all_instansi(db: Session = Depends(get_db)):
    try:
        rows = db.execute(select(Instansi)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    data = []
    for instansi in rows:
        data.append({
            "idInstansi": instansi[0].idInstansi,
            "nama": instansi[0].nama,
            "jenis": instansi[0].jenis,
            "alamat": instansi[0].alamat,
        })
    return {"instansi": data}

# show instansi by idInstansi
@router.get('/instansi/{idInstansi}',status_code=200)
def show_instansi_by_id(idInstansi: int, response:Response, db: Session = Depends(get_db)):
    try:
        row = db.execute(select(Instansi).where(Instansi.idInstansi==idInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if not row:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"instansi tidak ditemukan"}

    instansi = row[0]
    data = {
        "idInstansi": instansi.idInstansi,
        "nama": instansi.nama,
        "jenis": instansi.jenis,
        "alamat": instansi.alamat,
    }
    return {"instansi": data}