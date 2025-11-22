from fastapi import APIRouter, Response, status, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete, update
from sqlalchemy import DateTime

from app.classmodel.Kegiatan import *

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token



router = APIRouter(prefix="/kegiatan", tags=["Kegiatan"])

@router.get("/", response_model=List[JSONKegiatanResponse])
def get_all_kegiatan(
    response: Response,
    user: Annotated[dict, Depends(validate_token)],  
    db: Session = Depends(get_db)
):
    Kegiatan_list = []
    data = []
    try:
        Kegiatan_list = db.execute(select(Kegiatan.idKegiatan,Kegiatan.nama,Kegiatan.deskripsi,Instansi.nama,Kegiatan.bakat_list,Kegiatan.minat_list,Kegiatan.idLampiran,Kegiatan.waktu,Kegiatan.nominal_TAK,Kegiatan.TAK_wajib).join(Kegiatan).where(Kegiatan.status_kegiatan=="approved")).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    if not Kegiatan_list:
        return []
    for k in Kegiatan_list:
        data.append({"idKegiatan":k[0],"nama":k[1],"deskripsi":k[2],"nama_instansi":k[3],"bakat":[4],"minat":[5],"idLampiran":[6],"waktu":[7],"nominal_TAK":k[8],"TAK_wajib":k[9]})
    
    return data

# upload kegiatan
@router.post('/upload',status_code=200)
def upload_kegiatan(request: JSONKegiatanCreate, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    # hanya AdminInstansi yang dapat mengupload kegiatan
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    # cari idAdminInstansi dan idInstansi berdasarkan username user
    try:
        query = db.execute(select(AdminInstansi.idAdminInstansi, AdminInstansi.idInstansi).where(AdminInstansi.username==user['username'])).first()
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
    # Admin pengawas hanya pada saat approval, tidak bisa pilih salah satu

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

@router.post('/edit/{id}',status_code=200)
def edit_kegiatan(id: int, request: JSONKegiatanUpdate, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    
    try:
        query = db.execute(select(AdminInstansi.idAdminInstansi).where(AdminInstansi.username==user['username'])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"admin instansi tidak ditemukan"}
    idAdminInstansi = query[0]

    try:
        exists = db.execute(select(Kegiatan.idKegiatan).where(
            Kegiatan.idKegiatan==id,
            Kegiatan.idAdminInstansi==idAdminInstansi
        )).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"kegiatan tidak ditemukan atau bukan milik anda"}

    try:
        waktu_dt = datetime.fromisoformat(request.waktu)
    except Exception:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"format waktu salah, gunakan ISO datetime"}

    try:
        db.execute(text("""
            UPDATE Kegiatan SET
                nama = :nama,
                deskripsi = :deskripsi,
                waktu = :waktu,
                nominal_TAK = :nominal_TAK,
                TAK_wajib = :TAK_wajib,
                idLampiran = :idLampiran
            WHERE idKegiatan = :id
        """), {
            "nama": request.nama,
            "deskripsi": request.deskripsi,
            "waktu": waktu_dt,
            "nominal_TAK": request.nominal_TAK,
            "TAK_wajib": request.TAK_wajib,
            "idLampiran": request.idLampiran,
            "id": id
        })
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    return {"message":"kegiatan berhasil diupdate"}


@router.post('/{id}/delete',status_code=200)
def delete_kegiatan(id: int, user: Annotated[dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):

    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}

    try:
        query = db.execute(select(AdminInstansi.idAdminInstansi).where(AdminInstansi.username==user['username'])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"admin instansi tidak ditemukan"}
    idAdminInstansi = query[0]

    try:
        exists = db.execute(select(Kegiatan.idKegiatan).where(
            Kegiatan.idKegiatan==id,
            Kegiatan.idAdminInstansi==idAdminInstansi
        )).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not exists:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"kegiatan tidak ditemukan atau bukan milik anda"}

    try:
        db.execute(text("DELETE FROM Kegiatan WHERE idKegiatan = :id"), {"id": id})
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    return {"message":"kegiatan berhasil dihapus"}
