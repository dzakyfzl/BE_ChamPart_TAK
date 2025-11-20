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

MAX_AKUN_INSTANSI = 5

router = APIRouter(
    prefix="/account",
    tags=["Account"]
)

@router.post("/register/pengguna", status_code=200)
def register_user(pengguna: JSONPengguna, response: Response, db: Session = Depends(get_db)):
    try:
        v = validate_email(pengguna.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    try:
        existing_account = db.execute(text(f"SELECT COUNT(username) FROM Pengguna WHERE username='{pengguna.username}';")).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}
    
    access_token = create_token(pengguna.username,"Pengguna")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}

    salt = os.urandom(32).hex()
    prehash_password = pengguna.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try: 
        db.execute(insert(Pengguna).values(username=pengguna.username,email=pengguna.email,no_telp=pengguna.no_telp,prodi=pengguna.prodi,fakultas=pengguna.fakultas,salt=salt,hashed_password=hashed_password))
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
        existing_account = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.username == admin.username)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}
    
    access_token = create_token(admin.username,"AdminPengawas")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    salt = os.urandom(32).hex()
    prehash_password = admin.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    try:
        db.execute(insert(AdminPengawas).values(username=admin.username,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password))
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
        query = db.execute(select(Instansi.username).select_from(Instansi).where(Instansi.idInstansi==admin.idInstansi)).first()
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

    access_token = create_token(admin.username,"AdminInstansi")
    if access_token == "Error":
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

    access_token = create_token(query[0],akun.role)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    return {"message":"berhasil login","token":access_token}
    
@router.get("/get", status_code=200)
def info_akun(response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        if user["role"] == "Pengguna":
            query = db.execute(select(Pengguna.email,Pengguna.no_telp,Pengguna.fakultas,Pengguna.prodi).select_from(Pengguna).where(Pengguna.username==user['username'])).first()
        elif user["role"] == "AdminPengawas":
            query = db.execute(select(AdminPengawas.email,AdminPengawas.jabatan).select_from(AdminPengawas).where(AdminPengawas.username==user['username'])).first()
        elif user["role"] == "AdminInstansi":
            query = db.execute(select(AdminInstansi.email,AdminInstansi.jabatan,AdminInstansi.idInstansi).select_from(AdminInstansi).where(AdminInstansi.username==user['username'])).first()
            query2 = db.execute(select(Instansi.nama).select_from(Instansi).where(Instansi.idInstansi==query[2]))
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
    

@router.post("/admin/pengawas/edit", status_code=200)
def edit_akun_admin_pengawas(admin:JSONAdminPengawas, response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.username == admin.username)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"username sudah ada, silahkan coba yang lain"}

    access_token = create_token(admin.username,"AdminPengawas")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    try:
        db.execute(update(AdminPengawas).where(AdminPengawas.username==user["username"]).values(username=admin.username,email=admin.email,jabatan=admin.jabatan))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"akun telah berhasil diedit","token":access_token}

@router.post("/admin/instansi/edit", status_code=200)
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
    if existing_account[0][0] != 0:
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

@router.post("/pengguna/edit", status_code=200)
def edit_akun_pengguna(pengguna:JSONPengguna, response:Response, user: Annotated[dict, Depends(validate_token)],db:Session = Depends(get_db)):
    try:
        v = validate_email(pengguna.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    try:
        existing_account = db.execute(select(func.count('*')).select_from(Pengguna).where(Pengguna.username == pengguna.username)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"username sudah ada, silahkan coba yang lain"}

    access_token = create_token(pengguna.username,"AdminPengawas")
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    try:
        db.execute(update(Pengguna).where(Pengguna.username==user["username"]).values(username=pengguna.username,email=pengguna.email,no_telp=pengguna.no_telp,fakultas=pengguna.fakultas,prodi=pengguna.prodi))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"message":"akun telah berhasil diedit","token":access_token}

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