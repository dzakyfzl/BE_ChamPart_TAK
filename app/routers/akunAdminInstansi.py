from fastapi import APIRouter, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete, update

from app.classmodel.Account import JSONUpdatePassword
from app.classmodel.AdminInstansi import JSONCalonAdminInstansi
from app.database.models.calonAdminInstansi import CalonAdminInstansi
from ..database.models.refreshToken import RefreshToken

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..auth.jwt_auth import create_refresh_token, create_token
from ..depedency import validate_token
from ..security.adminPass import verif_pass
from email_validator import validate_email, EmailNotValidError
import os
import hashlib

MAX_AKUN_INSTANSI = 5

router = APIRouter(
    prefix="/account/admin-instansi",
    tags=["Account Admin Instansi"]
)

@router.post('/register',status_code=200)
def register_adminI(admin :JSONAdminInstansi, response:Response, db:Session = Depends(get_db)):
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.username == admin.username)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}
    
    existed_passkey = None
    try:
        existed_passkey = db.execute(select(Passkey.isiPasskey).select_from(Passkey).where(Passkey.idInstansi == admin.idInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not existed_passkey:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"instansi tidak ditemukan"}
    
    query = None
    try:
        query = db.execute(select(Instansi.nama).select_from(Instansi).where(Instansi.idInstansi==admin.idInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if not verif_pass(admin.passkey,admin.email,query[0],existed_passkey[0]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"passkey salah!"}

    try:
        verif_jumlah_admin_instansi = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.idInstansi == admin.idInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if verif_jumlah_admin_instansi[0] >= MAX_AKUN_INSTANSI:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message":"Jumlah akun sudah melebiihi maksimum"}

    try:
        db.execute(delete(RefreshToken).where(RefreshToken.username==admin.username))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    access_token = create_token(admin.username,"AdminInstansi")
    refresh_token = create_refresh_token(admin.username,"AdminInstansi")
    try:
        db.execute(insert(RefreshToken).values(username=admin.username,isi=refresh_token))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if access_token == "Error" or refresh_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    salt = os.urandom(32).hex()
    prehash_password = admin.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try:
        db.execute(insert(AdminInstansi).values(username=admin.username,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password,idInstansi=admin.idInstansi))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    try:
        db.execute(delete(Passkey).where(Passkey.isiPasskey==existed_passkey))
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
    
    return {"message":"akun telah dibuat","access_token":access_token,"refresh_token":refresh_token}

@router.post("/edit", status_code=200)
def edit_akun_admin_instansi(admin:JSONAdminInstansi, response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.username == admin.username)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"username sudah ada, silahkan coba yang lain"}

    access_token = create_token(admin.username,"AdminPengawas")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    try:
        db.execute(update(AdminInstansi).where(AdminInstansi.username==user["username"]).values(username=admin.username,email=admin.email,jabatan=admin.jabatan))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"akun telah berhasil diedit","token":access_token}

@router.post("/create-new", status_code=200)
def ajukan_akun_admin_instansi_baru(request:JSONCalonAdminInstansi, response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    try:
        v = validate_email(request.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    query = None
    try:
        query = db.execute(select(AdminInstansi.idInstansi).where(AdminInstansi.username==user["username"])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"User tidak terdaftar pada instansi manapun"}

    try:
        db.execute(insert(CalonAdminInstansi).values(email=request.email,idInstansi=query[0]))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":f"akun dengan email {request.email} telah berhasil diajukan, kami akan mengirimkan email kepada email yang bersangkutan"}

@router.get("/get-instansi",status_code=200)
def inikah_my_instansi(response:Response,user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    query = None
    query2 = None
    
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    
    try:
        query2 = db.execute(select(AdminInstansi.idInstansi).where(AdminInstansi.username==user["username"])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query2:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda bukan admin dari instansi manapun"}
    
    try:
        query = db.execute(select(Instansi.nama,Instansi.alamat,Instansi.jenis,Instansi.idLampiran).where(Instansi.idInstansi==query2[0])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        return{"message":"Instansi kosong"}


    return {"message":"data instansi berhasil diperoleh", "data":{"nama":query[0],"alamat":query[1],"jenis":query[2],"idLampiran":query[3]}}

