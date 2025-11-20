from fastapi import APIRouter, Response, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, delete

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token
from ..security.adminPass import generate_pass

router = APIRouter(
    prefix="/approve",
    tags=["Approval"]
)

@router.post('/instansi', status_code=200)
def approve_pendaftaran_instansi(
    request: JSONApproveCalonInstansi,
    user: Annotated[dict, Depends(validate_token)],
    response: Response,
    db: Session = Depends(get_db)
):
    if user["role"] != "AdminPengawas":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "anda tidak dapat mengunakan layanan ini"}

    # Ambil data calon instansi
    calon = db.execute(
        select(CalonInstansi).where(CalonInstansi.idCalonInstansi == request.idCalonInstansi)
    ).first()
    if not calon:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "calon instansi tidak ditemukan"}

    calon_instansi = calon[0]

    if request.isApproved:
        if calon_instansi.status == "baru":
            # Buat instansi baru
            try:
                db.execute(
                    insert(Instansi).values(
                        nama=calon_instansi.nama,
                        jenis=calon_instansi.jenis,
                        alamat=calon_instansi.alamat,
                        idLampiran=None  # atau sesuai kebutuhan
                    )
                )
                db.commit()
            except Exception as e:
                print(f"ERROR : {e}")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"message": "gagal membuat instansi baru"}
            return {"message": "instansi baru berhasil diapprove dan dibuat"}
        elif calon_instansi.status == "edit":
            # Cari instansi berdasarkan email_pengaju
            admin_instansi = db.execute(
                select(AdminInstansi).where(AdminInstansi.email == calon_instansi.email_pengaju)
            ).first()
            if not admin_instansi:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "admin instansi tidak ditemukan"}
            id_instansi = admin_instansi[0].idInstansi
            try:
                db.execute(
                    Instansi.__table__.update()
                    .where(Instansi.idInstansi == id_instansi)
                    .values(
                        nama=calon_instansi.nama,
                        jenis=calon_instansi.jenis,
                        alamat=calon_instansi.alamat
                    )
                )
                db.commit()
            except Exception as e:
                print(f"ERROR : {e}")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"message": "gagal update instansi"}
            return {"message": "instansi berhasil diupdate"}
    else:
        return {"message": "pengajuan tidak diapprove"}


@router.post('/admin-instansi',status_code=200)
def approve_pendaftaran_instansi(request: JSONApproveAdmin,user: Annotated[dict, Depends(validate_token)], response : Response, db:Session = Depends(get_db)):

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
    
    message = {"message":f"sukses reject {request.email} dari instansi {query[0]}","passkey":"None"}
    if request.isApproved:
        hashed_passkey = generate_pass(request.unique_character,request.email,query[0])

        try:
            db.execute(insert(Passkey).values(isiPasskey=hashed_passkey,idInstansi=request.idInstansi))
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
        message = {"message":f"sukses mengapprove {request.email} dari instansi {query[0]}","passkey":request.unique_character}

    return message