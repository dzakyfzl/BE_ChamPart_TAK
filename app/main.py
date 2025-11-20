from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated  
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete
from sqlalchemy.exc import *
from .database.database import get_db, SessionLocal
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
from .data.minatbakat import minat, bakat
from .auth.jwt_auth import create_token, decode_token
import os
import hashlib
from email_validator import validate_email, EmailNotValidError
from contextlib import asynccontextmanager
from datetime import datetime

Base.metadata.create_all(bind=engine)

# Ketika Program pertama kali dijalankan, apa yang ingin dilakukan
@asynccontextmanager
async def lifespan(app: FastAPI):

    # mengisi minat bakat pada database
    db = SessionLocal()

    count_m = []
    count_b = []

    # Cek apakah database kosong
    try:
        count_m = db.execute(select(func.count("*")).select_from(Minat)).first()
        count_b = db.execute(select(func.count("*")).select_from(Bakat)).first()
    except Exception as e:
        print("ERROR : ",e)
    
    if count_m[0] == 0 and count_b[0] == 0:
        try:
            db.execute(insert(Minat).values(minat))
            db.execute(insert(Bakat).values(bakat))
            db.commit()
        except Exception as e:
            print("EERROR : ",e)
    yield
    print("app dimatikan")

app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
MAX_AKUN_INSTANSI = 5




# Validasi Token
async def validate_token(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)) -> dict:
    payload = decode_token(token)
    query_isExist = None
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
        if payload["role"] == "Pengguna":
            query_isExist = db.execute(select(func.count('*')).select_from(Pengguna).where(Pengguna.nama==payload['sub'])).all()
        elif payload["role"] == "AdminPengawas":
            query_isExist = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.nama==payload['sub'])).all()
        elif payload["role"] == "AdminInstansi":
            query_isExist = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.nama==payload['sub'])).all()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role tidak valid",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Masalah pada database",
        )
    if query_isExist[0][0] == 0:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Pengguna Tidak ada",
            )
    user["nama"] = payload['sub']
    user["role"] = payload["role"]
    
    
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
    access_token = create_token(pengguna.nama,"Pengguna")
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
    access_token = create_token(admin.nama,"AdminPengawas")
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
sadasdadadad
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
    
    
    # Memeriksa apakah passkey dan instansi valid
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
    
    # Ambil nama instansi dari database 
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
    
    
    # Memeriksa apakah instansi sudah memiliki admin > maksimal_akun
    try:
        verif_jumlah_admin_instansi = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.idInstansi == admin.idInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if verif_jumlah_admin_instansi[0] >= MAX_AKUN_INSTANSI:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message":"Jumlah akun sudah melebiihi maksimum"}

    # Membuat akses token
    access_token = create_token(admin.nama,"AdminInstansi")
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
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # Menghapus Passkey di Database
    try:
        db.execute(delete(Passkey).where(Passkey.isiPasskey==existed_passkey))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # Atomicity Transaksi
    try:
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


@app.post('/login',status_code=200)
def login_le(akun:JSONLogin, response:Response,db:Session = Depends(get_db)):
    # Validasi Email
    try:
        v = validate_email(akun.email)
    except EmailNotValidError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"syntax email salah"}


    # Validasi Role
    query = None
    stmt = None
    try:
        if akun.role == 'Pengguna':
            stmt = select(Pengguna.nama,Pengguna.salt,Pengguna.hashed_password).select_from(Pengguna).where(Pengguna.email==akun.email)
        elif akun.role == 'AdminPengawas':
            stmt = select(AdminInstansi.nama,AdminInstansi.salt,AdminInstansi.hashed_password).select_from(AdminInstansi).where(AdminInstansi.email==akun.email)
        elif akun.role == 'AdminPengawas':
            stmt = select(AdminPengawas.nama,AdminPengawas.salt,AdminPengawas.hashed_password).select_from(AdminPengawas).where(AdminPengawas.email==akun.email)
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"akun di role ini tidak ditemukan"}

        # Ambil Nama
        query = db.execute(stmt).first()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    #Apakah user ada atau tidak
    if query == None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"akun tidak ditemukan"}
    
    # Validasi Password
    prehash_password = akun.password + query[1]
    hashed_input_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()
    if hashed_input_password != query[2]:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"password salah"}

    # Membuat akses token
    access_token = create_token(query[0],akun.role)
    if access_token == "Error":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"message":"tidak bisa generate token, Harap coba lagi"}
    
    # Sukses
    return {"message":"berhasil login","token":access_token}


# APPROVE

@app.post('/approve/instansi',status_code=200)
def approve_pendaftaran_instansi(request: JSONApproveInstansi,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):
    """
        Jika **Approve**, isilah idInstansi \n
        Jika **Reject**, isilah idInstansi dengan 0 pada frontend 
    """
    # Validasi role pengguna
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    
    # Cek apakah calon instansi terdaftar
    query = None
    try:
        query = db.execute(select(CalonInstansi.nama,CalonInstansi.jenis,CalonInstansi.alamat,CalonInstansi.email_pengaju).select_from(CalonInstansi).where(CalonInstansi.idCalonInstansi==request.idCalonInstansi)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"instansi tidak ada pada daftar calon"}
    
    # Jika Diapprove, maka ditambahkan ke dalam tabel
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
        
    
    # Hapus dari CalonInstansi
    try:
        db.execute(delete(CalonInstansi).where(CalonInstansi.idCalonInstansi==request.idCalonInstansi))
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # Atomicity Transaksi
    try:
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    # Sukses
    return message

@app.post('/approve/admin-instansi',status_code=200)
def approve_pendaftaran_instansi(request: JSONApproveAdmin,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):
    """
        Jika **Approve**, isilah unique_character \n
        Jika **Reject**, isilah unique_character dengan "-" pada frontend 
    """
    # Validasi role pengguna
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    
    # Cek apakah instansi ada pada database
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
    
    # Jika Diapprove, maka akan dibuatkan passkey
    message = {"message":f"sukses reject {request.email} dari instansi {query[0]}","passkey":"None"}
    if request.isApproved:
        # Buat Passkey
        hashed_passkey = generate_pass(request.unique_character,request.email,query[0])

        # Simpan Passkey ke database
        try:
            db.execute(insert(Passkey).values(isiPasskey=hashed_passkey,idInstansi=request.idInstansi))
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
        message = {"message":f"sukses mengapprove {request.email} dari instansi {query[0]}","passkey":request.unique_character}

    # Sukses
    return message


# Kegiatan endpoints


@app.post('/kegiatan/upload',status_code=200)
def upload_kegiatan(request: JSONKegiatan, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    # hanya AdminInstansi yang dapat mengupload kegiatan
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    # cari idAdminInstansi dan idInstansi berdasarkan nama user
    try:
        query = db.execute(select(AdminInstansi.idAdminInstansi, AdminInstansi.idInstansi).where(AdminInstansi.nama==user['nama'])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"admin instansi tidak ditemukan"}

    idAdminInstansi = query[0]
    idInstansi = query[1]

    # tentukan idAdminPengawas: gunakan dari request jika ada, atau pilih salah satu admin pengawas yang tersedia
    idAdminPengawas = request.idAdminPengawas
    if not idAdminPengawas:
        try:
            ap = db.execute(select(AdminPengawas.idAdminPengawas)).first()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
        if not ap:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"tidak ada AdminPengawas tersedia, tidak dapat mengupload kegiatan"}
        idAdminPengawas = ap[0]

    # parse waktu
    try:
        waktu_dt = datetime.fromisoformat(request.waktu)
    except Exception:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"format waktu salah, gunakan ISO datetime"}

    # insert kegiatan dengan status default Pending
    try:
        db.execute(insert(Kegiatan).values(
            nama=request.nama,
            deskripsi=request.deskripsi,
            waktu=waktu_dt,
            nominal_TAK=request.nominal_TAK,
            TAK_wajib=request.TAK_wajib,
            status_kegiatan='Pending',
            waktuDiupload=func.now(),
            idAdminPengawas=idAdminPengawas,
            idAdminInstansi=idAdminInstansi,
            idInstansi=idInstansi,
            idLampiran=request.idLampiran
        ))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":"kegiatan berhasil diupload, status: Pending"}


@app.put('/kegiatan/{id}/status',status_code=200)
def change_kegiatan_status(id: int, request: JSONChangeStatus, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    # hanya AdminPengawas yang dapat mengubah status
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    # validasi status
    allowed = {"approved":"Approved","aproved":"Approved","pending":"Pending","denied":"Denied","rejected":"Denied"}
    key = request.status.strip().lower()
    if key not in allowed:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"status tidak valid, gunakan Approved/Pending/Denied"}
    normalized = allowed[key]

    # cek apakah kegiatan ada
    try:
        exists = db.execute(select(Kegiatan.idKegiatan).where(Kegiatan.idKegiatan==id)).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"kegiatan tidak ditemukan"}

    # update status
    try:
        db.execute(text("UPDATE Kegiatan SET status_kegiatan = :s WHERE idKegiatan = :id"), {"s":normalized, "id": id})
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":f"status kegiatan diubah menjadi {normalized}"}


def serialize_kegiatan(obj: Kegiatan) -> dict:
    return {
        "idKegiatan": obj.idKegiatan,
        "nama": obj.nama,
        "deskripsi": obj.deskripsi,
        "waktu": obj.waktu.isoformat() if obj.waktu else None,
        "nominal_TAK": obj.nominal_TAK,
        "TAK_wajib": bool(obj.TAK_wajib),
        "status_kegiatan": obj.status_kegiatan,
        "waktuDiupload": obj.waktuDiupload.isoformat() if obj.waktuDiupload else None,
        "idAdminPengawas": obj.idAdminPengawas,
        "idAdminInstansi": obj.idAdminInstansi,
        "idInstansi": obj.idInstansi,
        "idLampiran": obj.idLampiran
    }


@app.get('/kegiatan/show',status_code=200)
def show_approved_kegiatan(db: Session = Depends(get_db)):
    try:
        rows = db.execute(select(Kegiatan).where(Kegiatan.status_kegiatan=='Approved')).all()
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error pada sambungan database")

    data = []
    for r in rows:
        k = r[0]
        data.append(serialize_kegiatan(k))
    return {"kegiatan": data}


@app.get('/kegiatan/all',status_code=200)
def show_all_kegiatan(db: Session = Depends(get_db)):
    try:
        rows = db.execute(select(Kegiatan)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error pada sambungan database")

    data = []
    for r in rows:
        k = r[0]
        data.append(serialize_kegiatan(k))
    return {"kegiatan": data}