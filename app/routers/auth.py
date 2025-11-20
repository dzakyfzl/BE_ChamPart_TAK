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

MAX_AKUN_INSTANSI = 5

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register/pengguna", status_code=200)
def register_user(pengguna: JSONPengguna, response: Response, db: Session = Depends(get_db)):
    try:
        v = validate_email(pengguna.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    try:
        existing_account = db.execute(text(f"SELECT COUNT(nama) FROM Pengguna WHERE nama='{pengguna.nama}';")).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}
    
    access_token = create_token(pengguna.nama,"Pengguna")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}

    salt = os.urandom(32).hex()
    prehash_password = pengguna.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try: 
        db.execute(insert(Pengguna).values(nama=pengguna.nama,email=pengguna.email,no_telp=pengguna.no_telp,prodi=pengguna.prodi,fakultas=pengguna.fakultas,salt=salt,hashed_password=hashed_password))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"akun telah dibuat","token":access_token}

@router.post('/register/admin/pengawas',status_code=200)
def register_adminP(admin :JSONAdminPengawas, response:Response, db:Session = Depends(get_db)):
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.nama == admin.nama)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}
    
    access_token = create_token(admin.nama,"AdminPengawas")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    salt = os.urandom(32).hex()
    prehash_password = admin.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try:
        db.execute(insert(AdminPengawas).values(nama=admin.nama,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"akun telah dibuat","token":access_token}

@router.post('/register/admin/instansi',status_code=200)
def register_adminI(admin :JSONAdminInstansi, response:Response, db:Session = Depends(get_db)):
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.nama == admin.nama)).all()
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

    access_token = create_token(admin.nama,"AdminInstansi")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    salt = os.urandom(32).hex()
    prehash_password = admin.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try:
        db.execute(insert(AdminInstansi).values(nama=admin.nama,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password,idInstansi=admin.idInstansi))
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
    
    return {"message":"akun telah dibuat","token":access_token}

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

@router.post('/login',status_code=200)
def login(akun:JSONLogin, response:Response,db:Session = Depends(get_db)):
    try:
        v = validate_email(akun.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah"}

    query = None
    stmt = None
    try:
        if akun.role == 'Pengguna':
            stmt = select(Pengguna.nama,Pengguna.salt,Pengguna.hashed_password).select_from(Pengguna).where(Pengguna.email==akun.email)
        elif akun.role == 'AdminInstansi':
            stmt = select(AdminInstansi.nama,AdminInstansi.salt,AdminInstansi.hashed_password).select_from(AdminInstansi).where(AdminInstansi.email==akun.email)
        elif akun.role == 'AdminPengawas':
            stmt = select(AdminPengawas.nama,AdminPengawas.salt,AdminPengawas.hashed_password).select_from(AdminPengawas).where(AdminPengawas.email==akun.email)
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"akun di role ini tidak ditemukan"}

        query = db.execute(stmt).first()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    if query == None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"akun tidak ditemukan"}
    
    prehash_password = akun.password + query[1]
    hashed_input_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()
    if hashed_input_password != query[2]:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"password salah"}

    access_token = create_token(query[0],akun.role)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    return {"message":"berhasil login","token":access_token}
    
