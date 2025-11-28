from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from ..database.database import get_db
from ..database.models import *
from ..classmodel import *
from ..depedency import validate_token

router = APIRouter(prefix="/simpan", tags=["Simpan Kegiatan"])

@router.post("/", status_code=200)
def simpan_kegiatan(
    request: JSONSimpanRequest,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    if user["role"] != "Pengguna": 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menyimpan kegiatan"
        )

    try:
        pengguna = db.execute(
            select(Pengguna).where(Pengguna.username == user["username"])
        ).scalar_one_or_none()
        
        if not pengguna:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengguna tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil data pengguna"
        )

    try:
        kegiatan = db.execute(
            select(Kegiatan).where(Kegiatan.idKegiatan == request.idKegiatan)
        ).scalar_one_or_none()

        if not kegiatan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kegiatan tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validasi kegiatan"
        )
    
    try:
        already_saved = db.execute(
            select(Simpan).where(
                Simpan.idPengguna == pengguna.idPengguna,
                Simpan.idKegiatan == request.idKegiatan
            )
        ).scalar_one_or_none()
        
        if already_saved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kegiatan sudah disimpan sebelumnya"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cek data simpan"
        )
    
    try:
        new_simpan = Simpan(
            idPengguna=pengguna.idPengguna,
            idKegiatan=request.idKegiatan,
            waktu=datetime.utcnow()
        )
        db.add(new_simpan)
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error menyimpan kegiatan"
        )
    
    return {"message": "Kegiatan berhasil disimpan"}


@router.get("/", response_model=JSONSimpanList, status_code=200)
def get_semua_simpan(
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat melihat kegiatan tersimpan"
        )

    try:
        pengguna = db.execute(
            select(Pengguna).where(Pengguna.username == user["username"])
        ).scalar_one_or_none()
        
        if not pengguna:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengguna tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil data pengguna"
        )

    try:
        now = datetime.now()
        simpan_list = pengguna.simpan_kegiatan
        
        kegiatan_list = [
            JSONSimpanResponse(
                idKegiatan=s.kegiatan.idKegiatan,
                nama_kegiatan=s.kegiatan.nama,
                deskripsi=s.kegiatan.deskripsi,
                waktu_kegiatan=s.kegiatan.waktu,
                nominal_TAK=s.kegiatan.nominal_TAK,
                TAK_wajib=s.kegiatan.TAK_wajib,
                status_kegiatan=s.kegiatan.status_kegiatan,
                nama_instansi=s.kegiatan.instansi.nama,
                waktu_disimpan=s.waktu
            )
            for s in simpan_list
            if s.kegiatan.status_kegiatan == "approved" and s.kegiatan.waktu > now
        ]

        kegiatan_list.sort(key=lambda x: x.waktu_kegiatan)

        return JSONSimpanList(
            total=len(kegiatan_list),
            kegiatan=kegiatan_list
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil kegiatan tersimpan"
        )
    

@router.get("/history", response_model=JSONSimpanList, status_code=200, summary="History Kegiatan Tersimpan")
def get_history_simpan(
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat melihat history"
        )

    try:
        pengguna = db.execute(
            select(Pengguna).where(Pengguna.username == user["username"])
        ).scalar_one_or_none()
        
        if not pengguna:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengguna tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil data pengguna"
        )
    try:
        now = datetime.now()
        simpan_list = pengguna.simpan_kegiatan
        
        kegiatan_list = [
            JSONSimpanResponse(
                idKegiatan=s.kegiatan.idKegiatan,
                nama_kegiatan=s.kegiatan.nama,
                deskripsi=s.kegiatan.deskripsi,
                waktu_kegiatan=s.kegiatan.waktu,
                nominal_TAK=s.kegiatan.nominal_TAK,
                TAK_wajib=s.kegiatan.TAK_wajib,
                status_kegiatan=s.kegiatan.status_kegiatan,
                nama_instansi=s.kegiatan.instansi.nama,
                waktu_disimpan=s.waktu
            )
            for s in simpan_list
            if s.kegiatan.waktu <= now  
        ]
        
        kegiatan_list.sort(key=lambda x: x.waktu_kegiatan, reverse=True)

        return JSONSimpanList(
            total=len(kegiatan_list),
            kegiatan=kegiatan_list
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil history kegiatan"
        )
    
@router.delete("/{idKegiatan}", status_code=200)
def hapus_simpan(
    idKegiatan: int,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menghapus kegiatan tersimpan"
        )

    try:
        pengguna = db.execute(
            select(Pengguna).where(Pengguna.username == user["username"])
        ).scalar_one_or_none()
        
        if not pengguna:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengguna tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil data pengguna"
        )

    try:
        simpan = db.execute(
            select(Simpan).where(
                Simpan.idPengguna == pengguna.idPengguna,
                Simpan.idKegiatan == idKegiatan
            )
        ).scalar_one_or_none()
        
        if not simpan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kegiatan tersimpan tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cek data simpan"
        )

    try:
        db.delete(simpan)
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error menghapus kegiatan tersimpan"
        )
    
    return {"message": "Kegiatan berhasil dihapus dari simpan"}