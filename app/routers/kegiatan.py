from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token

router = APIRouter(prefix="/kegiatan", tags=["Kegiatan"])

@router.get("/", response_model=List[JSONKegiatanResponse])
def get_all_kegiatan(
    user: Annotated[dict, Depends(validate_token)],  
    db: Session = Depends(get_db)
):
    Kegiatan_list = db.query(Kegiatan).all()
    if not Kegiatan_list:
        return []

    return Kegiatan_list

# upload kegiatan
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

# approval kegiatan
@app.put('/kegiatan/{id}/approval',status_code=200)
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


# show kegiatan berdasarkan status_kegiatan yang sudah Approved
@app.get('/kegiatan/showApprovec',status_code=200)
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

# show all kegiatan
@app.get('/kegiatan/showAll',status_code=200)
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

# edit kegiatan
@app.put('/kegiatan/{id}/edit',status_code=200)
def edit_kegiatan(id: int, request: JSONKegiatanEdit, user: Annotated
    #   yang bisa mengedit hanya AdminInstansi yang mengupload kegiatan tersebut
    [dict, Depends(validate_token)], response: Response, db: Session = Depends(get_db)):
    if user["role"] != "AdminInstansi":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda tidak dapat mengunakan layanan ini"}
    # cari idAdminInstansi berdasarkan nama user
    try:
        query = db.execute(select(AdminInstansi.idAdminInstansi).where(AdminInstansi.nama==user['nama'])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"admin instansi tidak ditemukan"}
    idAdminInstansi = query[0]
    # cek apakah kegiatan ada dan dimiliki oleh admin instansi tersebut
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
    # parse waktu
    try:
        waktu_dt = datetime.fromisoformat(request.waktu)
    except Exception:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"format waktu salah, gunakan ISO datetime"}
    # update kegiatan
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