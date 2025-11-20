from fastapi import APIRouter, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete, update

from app.classmodel.Account import JSONUpdatePassword

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..auth.jwt_auth import create_token
from ..depedency import validate_token
from ..security.adminPass import verif_pass
from email_validator import validate_email, EmailNotValidError
import os
import hashlib

router = APIRouter(
    prefix="/instansi",
    tags=["Instansi"]
)

@router.post('/register',status_code=200)
def register_instansi(instansi :JSONCalonInstansi, response:Response, db:Session = Depends(get_db)):
    try:
        v = validate_email(instansi.email_pengaju)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    try:
        db.execute(insert(CalonInstansi).values(nama=instansi.nama,jenis=instansi.jenis,alamat=instansi.alamat,email_pengaju=instansi.email_pengaju,jenis_calon="baru"))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":"instansi berhasil diajukan dan dalam proses verifikasi, cek email secara berkala"}

@router.post("/edit",status_code=200)
def ajukan_edit_instansi(instansi:JSONCalonInstansi,response:Response,user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    try:
        v = validate_email(instansi.email_pengaju)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    try:
        db.execute(insert(CalonInstansi).values(nama=instansi.nama,jenis=instansi.jenis,alamat=instansi.alamat,email_pengaju=instansi.email_pengaju,jenis_calon="edit"))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":"instansi berhasil diajukan,tunggu hingga diapprove"}