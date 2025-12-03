from fastapi import APIRouter, Response, status, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete, update

from app.classmodel.Account import JSONPassword, JSONUpdatePassword

from ..database.database import get_db

from ..database.models import * 
from ..database.models.refreshToken import RefreshToken
from ..classmodel import *

from ..auth.jwt_auth import create_token, create_refresh_token
from ..depedency import validate_token
from ..security.adminPass import verif_pass
from email_validator import validate_email, EmailNotValidError
import os
import hashlib

MAX_AKUN_INSTANSI = 5

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)

@router.post('/login',status_code=200)
def login(akun:JSONLogin, response:Response,db:Session = Depends(get_db)):
    
    query = None
    stmt = None
    try:
        if akun.role == 'Pengguna':
            stmt = select(Pengguna.username,Pengguna.salt,Pengguna.hashed_password).select_from(Pengguna).where(Pengguna.username==akun.username)
        elif akun.role == 'AdminInstansi':
            stmt = select(AdminInstansi.username,AdminInstansi.salt,AdminInstansi.hashed_password).select_from(AdminInstansi).where(AdminInstansi.username==akun.username)
        elif akun.role == 'AdminPengawas':
            stmt = select(AdminPengawas.username,AdminPengawas.salt,AdminPengawas.hashed_password).select_from(AdminPengawas).where(AdminPengawas.username==akun.username)
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
    
    try:
        db.execute(delete(RefreshToken).where(RefreshToken.username==query[0]))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    access_token = create_token(query[0],akun.role)
    refresh_token = create_refresh_token(query[0],akun.role)
    try:
        db.execute(insert(RefreshToken).values(username=query[0],isi=refresh_token))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if access_token == "Error" or refresh_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    return {"message":"berhasil login","access_token":access_token,"refresh_token":refresh_token}
    
@router.get("/get", status_code=200)
def info_akun(response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    query2=None
    try:
        if user["role"] == "Pengguna":
            query = db.execute(select(Pengguna.email,Pengguna.no_telp,Pengguna.fakultas,Pengguna.prodi).select_from(Pengguna).where(Pengguna.username==user['username'])).first()
        elif user["role"] == "AdminPengawas":
            query = db.execute(select(AdminPengawas.email,AdminPengawas.jabatan).select_from(AdminPengawas).where(AdminPengawas.username==user['username'])).first()
        elif user["role"] == "AdminInstansi":
            query = db.execute(select(AdminInstansi.email,AdminInstansi.jabatan,AdminInstansi.idInstansi).select_from(AdminInstansi).where(AdminInstansi.username==user['username'])).first()
            query2 = db.execute(select(Instansi.nama).select_from(Instansi).where(Instansi.idInstansi==query[2])).first()
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST,
            return {"message":"role tidak valid"}

    except Exception:
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        return {"message":"Masalah pada sambungan database"}
    
    if not query and not query2:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"user tidak ditemukan"}
    
    if user["role"] == "Pengguna":
        return {"username":user["username"],"email":query[0],"no_telp":query[1],"fakultas":query[2],"prodi":query[3]}
    elif user["role"] == "AdminPengawas":
        return {"username":user["username"],"email":query[0],"jabatan":query[1]}
    elif user["role"] == "AdminInstansi":
        return {"username":user["username"],"email":query[0],"jabatan":query[1],"nama_instansi":query2[0]}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"role tidak valid"}

@router.post("/edit-password", status_code=200)
def edit_password(password: JSONUpdatePassword, response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        if user["role"] == 'Pengguna':
            stmt = select(Pengguna.username,Pengguna.salt,Pengguna.hashed_password).select_from(Pengguna).where(Pengguna.username==user["username"])
        elif user["role"] == 'AdminInstansi':
            stmt = select(AdminInstansi.username,AdminInstansi.salt,AdminInstansi.hashed_password).select_from(AdminInstansi).where(AdminInstansi.username==user["username"])
        elif user["role"] == 'AdminPengawas':
            stmt = select(AdminPengawas.username,AdminPengawas.salt,AdminPengawas.hashed_password).select_from(AdminPengawas).where(AdminPengawas.username==user["username"])
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
    
    prehash_input_password = password.password_lama + query[1]
    hashed_input_password = hashlib.sha256(prehash_input_password.encode('utf-8')).hexdigest()
    if hashed_input_password != query[2]:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"password salah"}
    
    salt = os.urandom(32).hex()
    prehash_password = password.password_baru + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try:
        if user["role"] == 'Pengguna':
            stmt = update(Pengguna).where(Pengguna.username==user["username"]).values(salt=salt,hashed_password=hashed_password)
        elif user["role"] == 'AdminInstansi':
            stmt = update(AdminInstansi).where(AdminInstansi.username==user["username"]).values(salt=salt,hashed_password=hashed_password)
        elif user["role"] == 'AdminPengawas':
            stmt = update(AdminPengawas).where(AdminPengawas.username==user["username"]).values(salt=salt,hashed_password=hashed_password)
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"akun di role ini tidak ditemukan"}

        db.execute(stmt)
        db.commit()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"berhasil mengganti password"}

@router.post("/delete", status_code=200)
def hapus_akun(password: JSONPassword, response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        if user["role"] == 'Pengguna':
            stmt = select(Pengguna.username,Pengguna.salt,Pengguna.hashed_password).select_from(Pengguna).where(Pengguna.username==user["username"])
        elif user["role"] == 'AdminInstansi':
            stmt = select(AdminInstansi.username,AdminInstansi.salt,AdminInstansi.hashed_password).select_from(AdminInstansi).where(AdminInstansi.username==user["username"])
        elif user["role"] == 'AdminPengawas':
            stmt = select(AdminPengawas.username,AdminPengawas.salt,AdminPengawas.hashed_password).select_from(AdminPengawas).where(AdminPengawas.username==user["username"])
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
    
    prehash_input_password = password.password + query[1]
    hashed_input_password = hashlib.sha256(prehash_input_password.encode('utf-8')).hexdigest()
    if hashed_input_password != query[2]:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"password salah"}

    try:
        if user["role"] == 'Pengguna':
            stmt = delete(Pengguna).where(Pengguna.username==user["username"])
        elif user["role"] == 'AdminInstansi':
            stmt = delete(AdminInstansi).where(AdminInstansi.username==user["username"])
        elif user["role"] == 'AdminPengawas':
            stmt = delete(AdminPengawas).where(AdminPengawas.username==user["username"])
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"akun di role ini tidak ditemukan"}

        db.execute(stmt)
        db.execute(delete(RefreshToken).where(RefreshToken.username==user["username"]))
        db.commit()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"berhasil menghapus akun"}

@router.get("/logout")
def logout_akun(response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        db.execute(delete(RefreshToken).where(RefreshToken.username==user["username"]))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    return {"message":"akun telah di logout"}