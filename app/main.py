from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated  
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete
from sqlalchemy.exc import *
from .database.database import get_db
from .database.database import Base, engine
from .security.adminPass import *
from .database.models.bakat import Bakat
from .database.models.pengguna import Pengguna
from .database.models.lampiran import Lampiran
from .database.models.kegiatan import Kegiatan
from .database.models.minat import Minat
from .database.models.instansi import Instansi
from .database.models.adminInstansi import AdminInstansi
from .database.models.adminPengawas import AdminPengawas
from .database.models.passkey import Passkey
from .database.models.calonInstansi import CalonInstansi 
from .database.models.minatKegiatan import minatKegiatan
from .database.models.minatPengguna import minatPengguna
from .database.models.bakatKegiatan import bakatKegiatan
from .database.models.bakatPengguna import bakatPengguna
from .classmodel.requestmodels import *
from .auth.jwt_auth import create_token, decode_token
import os
import hashlib
from email_validator import validate_email, EmailNotValidError



app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
MAX_AKUN_INSTANSI = 5

Base.metadata.create_all(bind=engine)

# Validasi Token
async def validate_token(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)) -> dict:
    payload = decode_token(token)
    user = {
        "nama":"",
        "role":""
    }
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        isPengguna = db.execute(select(func.count('*')).select_from(Pengguna).where(Pengguna.nama==payload['sub'])).all()
        isAdminPengawas = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.nama==payload['sub'])).all()
        isAdminInstansi = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.nama==payload['sub'])).all()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Masalah pada database",
        )
    user["nama"] = payload['sub']
    if isPengguna[0][0] == 1:
        user["role"] = "Pengguna"
    elif isAdminPengawas[0][0] == 1:
        user["role"] = "AdminPengawas"
    elif isAdminInstansi[0][0] == 1:
        user["role"] = "AdminInstansi"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun Tidak Ditemukan",
        )
    
    return user
        



# TEST ENDPOINT

@app.get("/",status_code=200)
def test(user: Annotated[dict, Depends(validate_token)]):
    return{"message":"Yahhoo~! token-mu valid","user":user}
    

# REGISTER ENDPOINT

@app.post("/register/pengguna", status_code=200)
def register_user(pengguna: JSONPengguna, response: Response, db: Session = Depends(get_db)):
    # Validasi Email
    try:
        v = validate_email(pengguna.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    # Cek apakah pengguna telah terdaftar
    try:
        existing_account = db.execute(text(f"SELECT COUNT(nama) FROM Pengguna WHERE nama='{pengguna.nama}';")).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}

    # Membuat akses token
    access_token = create_token(pengguna.nama)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    # Generate salt dan hash password
    salt = os.urandom(32).hex()
    prehash_password = pengguna.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()


    # Database insert
    try:
        db.execute(insert(Pengguna).values(nama=pengguna.nama,email=pengguna.email,no_telp=pengguna.no_telp,prodi=pengguna.prodi,fakultas=pengguna.fakultas,salt=salt,hashed_password=hashed_password))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    # Sukses
    return {"message":"akun telah dibuat","token":access_token}

@app.post('/register/pengguna/minat-bakat',status_code=200)
def register_minat_bakat_user(minatbakat: JSONMinatBakat, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    # periksa apakah lebih dari 0
    if not minatbakat.minat or not minatbakat.bakat:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"minat atau bakat kosong"}
    
    # periksa apakah angka
    for bakat in minatbakat.bakat:
        if type(bakat) is not int:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"format input salah"}
    for minat in minatbakat.minat:
        if type(minat) is not int:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"format input salah"}
    
    # cari ID User
    try:
        query_id_pengguna = db.execute(select(Pengguna.idPengguna).select_from(Pengguna).where(Pengguna.nama==user["nama"])).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query_id_pengguna:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"pengguna tidak ditemukan"}
    
    id_pengguna = query_id_pengguna[0][0]

    # eksekusi minat pada database
    data = []
    for minat in minatbakat.minat:
        data.append({"idPengguna":id_pengguna,"idMinat":minat})
    try: 
        db.execute(insert(minatPengguna).values(data))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # eksekusi bakat pada database
    data = []
    for bakat in minatbakat.bakat:
        data.append({"idPengguna":id_pengguna,"idBakat":bakat})
    try: 
        db.execute(insert(bakatPengguna).values(data))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # commit
    try:
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # sukses
    return {"message":"minat dan bakat telah sukses ditambahkan"}
    



@app.post('/register/admin/pengawas',status_code=200)
def register_adminP(admin :JSONAdminPengawas, response:Response, db:Session = Depends(get_db)):
    # Validasi Email
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    # Cek apakah pengguna telah terdaftar
    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.nama == admin.nama)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}

    # Membuat akses token
    access_token = create_token(admin.nama)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    # Generate salt dan hash password
    salt = os.urandom(32).hex()
    prehash_password = admin.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()


    # Database insert
    try:
        db.execute(insert(AdminPengawas).values(nama=admin.nama,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    # Sukses
    return {"message":"akun telah dibuat","token":access_token}

@app.post('/register/admin/instansi',status_code=200)
def register_adminI(admin :JSONAdminInstansi, response:Response, db:Session = Depends(get_db)):
    # Validasi Email
    try:
        v = validate_email(admin.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}
    
    # Cek apakah pengguna telah terdaftar
    try:
        existing_account = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.nama == admin.nama)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if existing_account[0][0] != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun sudah ada, harap untuk login"}
    
    
    # Memeriksa apakah passkey yang dimasukkan valid
    try:
        existed_passkey = db.execute(select(Passkey.isi).select_from(Passkey).where(Passkey.idInstansi == admin.idInstansi)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not existed_passkey:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"instansi tidak ditemukan"}
    if not verif_pass(admin.passkey,admin.idInstansi,existed_passkey):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"passkey salah!"}
    
    
    # Memeriksa apakah instansi sudah memiliki admin > maksimal_akun
    try:
        verif_jumlah_admin_instansi = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.idInstansi == admin.idInstansi)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if verif_jumlah_admin_instansi >= MAX_AKUN_INSTANSI:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message":"Jumlah akun sudah melebiihi maksimum"}

    # Membuat akses token
    access_token = create_token(admin.nama)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    # Generate salt dan hash password
    salt = os.urandom(32).hex()
    prehash_password = admin.password + salt
    hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

    # Database insert
    try:
        db.execute(insert(AdminInstansi).values(nama=admin.nama,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password,idInstansi=admin.idInstansi))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # Menghapus Passkey di Database
    try:
        db.execute(delete(Passkey).where(Passkey.isiPasskey==existed_passkey))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    # Sukses
    return {"message":"akun telah dibuat","token":access_token}

@app.post('/register/instansi',status_code=200)
def register_instansi(instansi :JSONCalonInstansi, response:Response, db:Session = Depends(get_db)):
    # Validasi Email
    try:
        v = validate_email(instansi.email_pengaju)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah, harap masukkan yang benar"}

    # Masukkan ke database
    try:
        db.execute(insert(CalonInstansi).values(nama=instansi.nama,jenis=instansi.jenis,alamat=instansi.alamat,email_pengaju=instansi.email_pengaju))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # Sukses
    return {"message":"instansi berhasil diajukan dan dalam proses verifikasi, cek email secara berkala"}

# NOTE : Validasi Email di Frontend
@app.post('/login',status_code=200)
def login_le(akun:JSONAccount, response:Response,db:Session = Depends(get_db)):
    # Cek apakah pengguna menggunakan nama/email
    if akun.email != '-':
        stmt1 = select(Pengguna).where(Pengguna.email==akun.email)
        stmt2 = select(AdminInstansi).where(AdminInstansi.email==akun.email)
        stmt3 = select(AdminPengawas).where(AdminPengawas.email==akun.email)
    else:
        stmt1 = select(Pengguna).where(Pengguna.nama==akun.nama)
        stmt2 = select(AdminInstansi).where(AdminInstansi.nama==akun.nama)
        stmt3 = select(AdminPengawas).where(AdminPengawas.nama==akun.nama)
    try:
        pengguna = db.execute(stmt1).all()
        admin_pengawas = db.execute(stmt2).all()
        admin_instansi = db.execute(stmt3).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    print(admin_instansi,admin_pengawas,pengguna)
    if not admin_instansi and not admin_pengawas and not pengguna:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"akun tidak ditemukan"}
    
    # Membuat akses token
    access_token = create_token(akun.nama)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    # Sukses
    return {"message":"berhasil login (DEV_DEBUG)","token":access_token}