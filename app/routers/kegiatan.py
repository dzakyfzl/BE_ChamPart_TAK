from fastapi import APIRouter, Response, status, Depends,Query
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete, update
from datetime import datetime

from app.classmodel.Kegiatan import *

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token



router = APIRouter(prefix="/kegiatan", tags=["Kegiatan"])

@router.get("/all", response_model=List[JSONKegiatanCard], summary="Get All Kegiatan")
def get_all_kegiatan(
    response: Response,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    try:
        kegiatan_list = db.execute(
            select(Kegiatan)
            .order_by(Kegiatan.waktuDiupload.desc())
        ).scalars().all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "error pada sambungan database"}

    if not kegiatan_list:
        return []

    data = []
    for k in kegiatan_list:
        data.append({
            "idKegiatan": k.idKegiatan,
            "nama": k.nama,
            "nama_instansi": k.instansi.nama,
            "TAK_wajib": k.TAK_wajib,
            "waktu": k.waktu,
            "waktuDiupload": k.waktuDiupload,
            "views": k.views,
            "minat": [{"idMinat": m.idMinat, "nama_minat": m.nama} for m in k.minat_list],
            "bakat": [{"idBakat": b.idBakat, "nama_bakat": b.nama} for b in k.bakat_list]
        })
    
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

@router.get("/filter", response_model=List[JSONKegiatanCard], summary="Filter & Search Kegiatan")
def filter_search_kegiatan(
    response: Response,
    user: Annotated[dict, Depends(validate_token)],
    search: str = Query(default="", description="Cari berdasarkan nama kegiatan"),
    minat_ids: List[int] = Query(default=[], description="List ID minat"),
    bakat_ids: List[int] = Query(default=[], description="List ID bakat"),
    db: Session = Depends(get_db)
):
    now = datetime.now()
    
    if not minat_ids and not bakat_ids:
        try:
            query = select(Kegiatan).where(
                Kegiatan.status_kegiatan == "approved", 
                Kegiatan.waktu > now
            )
            
            if search:
                query = query.where(Kegiatan.nama.ilike(f"%{search}%"))
            
            kegiatan_list = db.execute(query).scalars().all()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "error pada sambungan database"}
    else:
        try:
            kegiatan_by_minat = set()
            if minat_ids:
                query = (
                    select(Kegiatan)
                    .join(minatKegiatan, Kegiatan.idKegiatan == minatKegiatan.c.idKegiatan)
                    .where(
                        Kegiatan.status_kegiatan == "approved",
                        Kegiatan.waktu > now,
                        minatKegiatan.c.idMinat.in_(minat_ids)
                    )
                )
                if search:
                    query = query.where(Kegiatan.nama.ilike(f"%{search}%"))
                
                result = db.execute(query).scalars().all()
                kegiatan_by_minat = set(result)
            
            kegiatan_by_bakat = set()
            if bakat_ids:
                query = (
                    select(Kegiatan)
                    .join(bakatKegiatan, Kegiatan.idKegiatan == bakatKegiatan.c.idKegiatan)
                    .where(
                        Kegiatan.status_kegiatan == "approved",
                        Kegiatan.waktu > now,
                        bakatKegiatan.c.idBakat.in_(bakat_ids)
                    )
                )
                if search:
                    query = query.where(Kegiatan.nama.ilike(f"%{search}%"))
                
                result = db.execute(query).scalars().all()
                kegiatan_by_bakat = set(result)

            kegiatan_list = list(kegiatan_by_minat | kegiatan_by_bakat)
            
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "error pada sambungan database"}

    if not kegiatan_list:
        return []

    data = []
    for k in kegiatan_list:
        data.append({
            "idKegiatan": k.idKegiatan,
            "nama": k.nama,
            "nama_instansi": k.instansi.nama,
            "TAK_wajib": k.TAK_wajib,
            "waktu": k.waktu,
            "waktuDiupload": k.waktuDiupload,
            "views": k.views,
            "minat": [{"idMinat": m.idMinat, "nama_minat": m.nama} for m in k.minat_list],
            "bakat": [{"idBakat": b.idBakat, "nama_bakat": b.nama} for b in k.bakat_list]
        })
    
    return data

@router.get("/fyp", response_model=List[JSONKegiatanCard], summary="For You Page")
def get_fyp_kegiatan(
    response: Response,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    now = datetime.now()
    
    if user["role"] != "Pengguna":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "Hanya pengguna yang dapat melihat FYP"}

    try:
        pengguna = db.execute(
            select(Pengguna).where(Pengguna.username == user["username"])
        ).scalar_one_or_none()
        
        if not pengguna:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Pengguna tidak ditemukan"}
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "error pada sambungan database"}

    minat_ids = [m.idMinat for m in pengguna.minat_list]
    bakat_ids = [b.idBakat for b in pengguna.bakat_list]

    if not minat_ids and not bakat_ids:
        try:
            kegiatan_list = db.execute(
                select(Kegiatan)
                .where(
                    Kegiatan.status_kegiatan == "approved",
                    Kegiatan.waktu > now
                )
                .order_by(Kegiatan.waktuDiupload.desc())
            ).scalars().all()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "error pada sambungan database"}
    else:
        try:
            kegiatan_by_minat = set()
            if minat_ids:
                result = db.execute(
                    select(Kegiatan)
                    .join(minatKegiatan, Kegiatan.idKegiatan == minatKegiatan.c.idKegiatan)
                    .where(
                        Kegiatan.status_kegiatan == "approved",
                        Kegiatan.waktu > now,
                        minatKegiatan.c.idMinat.in_(minat_ids)
                    )
                ).scalars().all()
                kegiatan_by_minat = set(result)
            
            kegiatan_by_bakat = set()
            if bakat_ids:
                result = db.execute(
                    select(Kegiatan)
                    .join(bakatKegiatan, Kegiatan.idKegiatan == bakatKegiatan.c.idKegiatan)
                    .where(
                        Kegiatan.status_kegiatan == "approved",
                        Kegiatan.waktu > now,
                        bakatKegiatan.c.idBakat.in_(bakat_ids)
                    )
                ).scalars().all()
                kegiatan_by_bakat = set(result)

            kegiatan_list = list(kegiatan_by_minat | kegiatan_by_bakat)
            kegiatan_list.sort(key=lambda x: x.waktuDiupload, reverse=True)
            
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "error pada sambungan database"}

    if not kegiatan_list:
        return []

    data = []
    for k in kegiatan_list:
        data.append({
            "idKegiatan": k.idKegiatan,
            "nama": k.nama,
            "nama_instansi": k.instansi.nama,
            "TAK_wajib": k.TAK_wajib,
            "waktu": k.waktu,
            "waktuDiupload": k.waktuDiupload,
            "views": k.views,
            "minat": [{"idMinat": m.idMinat, "nama_minat": m.nama} for m in k.minat_list],
            "bakat": [{"idBakat": b.idBakat, "nama_bakat": b.nama} for b in k.bakat_list]
        })
    
    return data

@router.get("/{idKegiatan}", response_model=JSONKegiatanDetail, summary="Get Detail Kegiatan")
def get_detail_kegiatan(
    idKegiatan: int,
    response: Response,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    
    try:
        kegiatan = db.execute(
            select(Kegiatan).where(Kegiatan.idKegiatan == idKegiatan)
        ).scalar_one_or_none()
        
        if not kegiatan:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Kegiatan tidak ditemukan"}
        
        kegiatan.views += 1
        db.commit()
        db.refresh(kegiatan)
        
        return {
            "idKegiatan": kegiatan.idKegiatan,
            "nama": kegiatan.nama,
            "deskripsi": kegiatan.deskripsi,
            "waktu": kegiatan.waktu,
            "nominal_TAK": kegiatan.nominal_TAK,
            "TAK_wajib": kegiatan.TAK_wajib,
            "status_kegiatan": kegiatan.status_kegiatan,
            "waktuDiupload": kegiatan.waktuDiupload,
            "views": kegiatan.views,
            "nama_instansi": kegiatan.instansi.nama,
            "lampiran": {
                "idLampiran": kegiatan.lampiran.idLampiran,
                "nama": kegiatan.lampiran.nama,
                "jenis": kegiatan.lampiran.jenis,
                "ukuran": kegiatan.lampiran.ukuran,
                "folder": kegiatan.lampiran.folder
            } if kegiatan.lampiran else None,
            "minat": [{"idMinat": m.idMinat, "nama_minat": m.nama} for m in kegiatan.minat_list],
            "bakat": [{"idBakat": b.idBakat, "nama_bakat": b.nama} for b in kegiatan.bakat_list]
        }
        
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "error pada sambungan database"}
