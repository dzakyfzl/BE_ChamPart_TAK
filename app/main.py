from fastapi import Depends, FastAPI, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func
from .database.database import get_db
from .database.database import Base, engine
from .database.models.bakat import Bakat
from .database.models.pengguna import Pengguna
from .database.models.lampiran import Lampiran
from .database.models.kegiatan import Kegiatan
from .database.models.minat import Minat
from .database.models.instansi import Instansi
from .database.models.adminInstansi import AdminInstansi
from .database.models.adminPengawas import AdminPengawas
from .classmodel.requestmodels import JSONPengguna, JSONAdminPengawas
from .auth.jwt_auth import create_token,decode_token
import os
import hashlib

app = FastAPI()

Base.metadata.create_all(bind=engine)

# TEST ENDPOINT
@app.get("/")
def get_all_bakat(db: Session = Depends(get_db)):
    try:
        bakat_list = db.query(Bakat).all()
        return {
            "status": "success",
            "data": [
                {
                    "idBakat": bakat.idBakat,
                    "nama": bakat.nama
                } 
                for bakat in bakat_list
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# REGISTER ENDPOINT

@app.post("/register/pengguna", status_code=200)
def register_user(pengguna: JSONPengguna, response: Response, db: Session = Depends(get_db)):
    # Cek apakah pengguna telah terdaftar
    existing_account = db.execute(text(f"SELECT COUNT(nama) FROM Pengguna WHERE nama='{pengguna.nama}';")).all()
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
    db.execute(insert(Pengguna).values(nama=pengguna.nama,email=pengguna.email,no_telp=pengguna.no_telp,prodi=pengguna.prodi,fakultas=pengguna.fakultas,salt=salt,hashed_password=hashed_password))
    db.commit()

    # Sukses
    return {"message":"akun telah dibuat","token":access_token}

@app.post('/register/admin/pengawas',status_code=200)
def register_adminP(admin :JSONAdminPengawas, response:Response, db:Session = Depends(get_db)):
    # Cek apakah pengguna telah terdaftar
    existing_account = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.nama == admin.nama)).all()

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
    db.execute(insert(AdminPengawas).values(nama=admin.nama,email=admin.email,jabatan=admin.jabatan,salt=salt,hashed_password=hashed_password))
    db.commit()

    # Sukses
    return {"message":"akun telah dibuat","token":access_token}