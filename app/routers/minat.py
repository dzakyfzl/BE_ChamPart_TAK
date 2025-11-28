from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, delete

from ..database.database import get_db
from ..database.models import *
from ..classmodel import *

from ..depedency import validate_token

router = APIRouter(prefix="/minat", tags=["Minat"])

@router.post("/pengguna", status_code=200)
def tambah_minat_pengguna(
    request: JSONMinatRequest,
    user : Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    
    if user["role"] != "Pengguna": 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menggunakan endpoint ini"
        )
    
    if not request.minat_id:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minat tidak boleh kosong"
        )
    
    for minat_id in request.minat_id:
        if type(minat_id) is not int:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format input salah, ID harus berupa integer"
            )
        
    try : 
        query_id = db.execute(
            select(Pengguna.idPengguna)
            .where(Pengguna.username == user["username"])
        ).first()
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error pada sambungan database"
        )
    
    if not query_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
    
    id_pengguna = query_id[0]

    try:
        existing_minat = db.execute(
            select(Minat.idMinat)
            .where(Minat.idMinat.in_(request.minat_id))
        ).all()
        existing_ids = [m[0] for m in existing_minat]
    
        invalid_ids = [mid for mid in request.minat_id if mid not in existing_ids]
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minat dengan ID {invalid_ids} tidak ditemukan"
            )  
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validasi minat"
        )

    data = [{"idPengguna": id_pengguna, "idMinat": minat_id} for minat_id in request.minat_id]

    try:
        db.execute(insert(minatPengguna).values(data))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error menyimpan minat"
        )
    
    return {"message": "Minat berhasil ditambahkan"}


@router.get("/pengguna", status_code=200)
def get_minat_pengguna(
    user : Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat melihat minatnya sendiri"
        )
    
    try:
        query_id = db.execute(
            select(Pengguna.idPengguna)
            .where(Pengguna.username == user["username"])
        ).first()

    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error pada sambungan database"
        )

    if not query_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
    
    id_pengguna = query_id[0]

    try:
        result = db.execute(
            select(Minat.idMinat, Minat.nama)
            .select_from(minatPengguna)
            .join(Minat, minatPengguna.c.idMinat == Minat.idMinat)
            .where(minatPengguna.c.idPengguna == id_pengguna)
        ).all()

        return {
            "minat": [{"idMinat": r[0], "nama": r[1]} for r in result]
        }
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil data minat"
        )
    
@router.delete("/pengguna", status_code=200)
def hapus_minat_pengguna(
    request: JSONMinatRequest,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menghapus minatnya sendiri"
        )
    
    if not request.minat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minat tidak boleh kosong"
        )
    
    for minat_id in request.minat_id:
        if type(minat_id) is not int:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format input salah, ID harus berupa integer"
            )
    
    try:
        query_id = db.execute(
            select(Pengguna.idPengguna)
            .where(Pengguna.username == user["username"])
        ).first()
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error pada sambungan database"
        )
    
    if not query_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
    
    id_pengguna = query_id[0]

    try:
        existing_minat = db.execute(
            select(minatPengguna.c.idMinat)
            .where(
                minatPengguna.c.idPengguna == id_pengguna,
                minatPengguna.c.idMinat.in_(request.minat_id)
            )
        ).all()
        existing_ids = [m[0] for m in existing_minat]
        
        invalid_ids = [mid for mid in request.minat_id if mid not in existing_ids]
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Minat dengan ID {invalid_ids} tidak ditemukan pada pengguna ini"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validasi minat"
        )
    
    try:
        db.execute(
            delete(minatPengguna)
            .where(
                minatPengguna.c.idPengguna == id_pengguna,
                minatPengguna.c.idMinat.in_(request.minat_id)
            )
        )
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error menghapus minat"
        )
    
    return {"message": f"Minat berhasil dihapus"}