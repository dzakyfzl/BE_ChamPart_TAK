from fastapi import APIRouter, BackgroundTasks, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import and_, exists, insert, select, delete, text, update

from app.classmodel.Kegiatan import JSONChangeStatus
from app.database.models.calonAdminInstansi import CalonAdminInstansi
from app.depedency import send_email

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
        return {"message": "calon instansi tidak ditemukan"}

    calon_instansi = query

    if request.isApproved:
        try:
            db.execute(
                insert(Instansi).values(
                    nama=calon_instansi[0],
                    jenis=calon_instansi[1],
                    alamat=calon_instansi[2]
                )
            )
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "gagal membuat instansi baru"}
        return {"message": "instansi baru berhasil diapprove dan dibuat"}
    else:
        return {"message": "pengajuan tidak diapprove"}


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
def approve_pendaftaran_admin_instansi(request: JSONApproveAdmin,bg_tasks:BackgroundTasks,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):

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
    
    message = {"message":f"sukses reject {request.email} dari instansi {query[0]}"}
    if request.isApproved:
        hashed_passkey = generate_pass(request.unique_character,request.email,query[0])

        try:
            db.execute(insert(Passkey).values(isiPasskey=hashed_passkey,idInstansi=request.idInstansi))
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
        isi = f"Selamat, akun anda dengan email {request.email} telah diterima sebagai admin instansi pada {query[0]} \n\nPasskey : {request.unique_character} \n\nPERINGATAN : Jangan sebarkan Passkey ke siapapun \n\nAdmin instansi dapat melakukan :\n1. Menambah dan mengelola Kegiatan\n2. Mengedit properti instansi\n3. Melakukan pengelolaan akun pribadi\n\nSatu Instansi maksimal memiliki 5 akun Admin Instansi"
        bg_tasks.add_task(send_email,"CHAMPART -  Akun anda berhasil di approve",isi,request.email)
        message = {"message":f"sukses mengapprove {request.email} dari instansi {query[0]}"}
    try:
        db.execute(delete(CalonAdminInstansi).where(CalonAdminInstansi.email==request.email))
        db.commit()
    except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}

    return message

@router.post('/kegiatan/{id}',status_code=200)
def change_kegiatan_status(id: int, request: JSONChangeStatus, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    allowed = {"approved":"Approved","aproved":"Approved","pending":"Pending","denied":"Denied","rejected":"Denied"}
    key = request.status.strip().lower()
    if key not in allowed:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"status tidak valid, gunakan Approved/Pending/Denied"}
    normalized = allowed[key]

    try:
        exists = db.execute(select(Kegiatan.idKegiatan).where(Kegiatan.idKegiatan==id)).first()
        query = db.execute(select(AdminPengawas.idAdminPengawas).where(AdminPengawas.username==user["username"])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"kegiatan tidak ditemukan"}

    try:
        db.execute(text("UPDATE Kegiatan SET status_kegiatan = :s, idAdminInstansi = :idA WHERE idKegiatan = :id"), {"s":normalized,"idA":query[0], "id": id})
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    return {"message":f"status kegiatan diubah menjadi {normalized}"}