from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, delete

from ..database.database import get_db
from ..database.models import *
from ..classmodel import *

from ..depedency import validate_token

router = APIRouter(prefix="/bakat", tags=["Bakat"])

@router.post("/pengguna", status_code=200)
def tambah_bakat_pengguna(
    request: JSONBakatRequest,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menggunakan endpoint ini"
        )
    
    if not request.bakat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bakat tidak boleh kosong"
        )
    
    for bakat_id in request.bakat_id:
        if type(bakat_id) is not int:
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
        existing_bakat = db.execute(
            select(Bakat.idBakat)
            .where(Bakat.idBakat.in_(request.bakat_id))
        ).all()
        existing_ids = [b[0] for b in existing_bakat]

        invalid_ids = [bid for bid in request.bakat_id if bid not in existing_ids]
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bakat dengan ID {invalid_ids} tidak ditemukan"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validasi bakat"
        )
    data = [{"idPengguna": id_pengguna, "idBakat": bakat_id} for bakat_id in request.bakat_id]
    
    try:
        db.execute(insert(bakatPengguna).values(data))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error menyimpan bakat"
        )

    return {"message": "Bakat berhasil ditambahkan"}

@router.get("/pengguna", status_code=200)
def get_bakat_pengguna(
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menggunakan endpoint ini"
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
            select(Bakat.idBakat, Bakat.nama)
            .select_from(bakatPengguna)
            .join(Bakat, bakatPengguna.c.idBakat == Bakat.idBakat)
            .where(bakatPengguna.c.idPengguna == id_pengguna)
        ).all()
        return {
            "bakat": [{"idBakat": r[0], "nama": r[1]} for r in result]
        }
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error mengambil data bakat"
        )
    
@router.delete("/pengguna", status_code=200)
def hapus_bakat_pengguna(
    request: JSONBakatRequest,
    user: Annotated[dict, Depends(validate_token)],
    db: Session = Depends(get_db)
):
    if user["role"] != "Pengguna":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pengguna yang dapat menghapus bakatnya sendiri"
        )
    
    if not request.bakat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bakat tidak boleh kosong"
        )
    
    for bakat_id in request.bakat_id:
        if type(bakat_id) is not int:
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
        existing_bakat = db.execute(
            select(bakatPengguna.c.idBakat)
            .where(
                bakatPengguna.c.idPengguna == id_pengguna,
                bakatPengguna.c.idBakat.in_(request.bakat_id)
            )
        ).all()
        existing_ids = [b[0] for b in existing_bakat]
        
        invalid_ids = [bid for bid in request.bakat_id if bid not in existing_ids]
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bakat dengan ID {invalid_ids} tidak ditemukan pada pengguna ini"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validasi bakat"
        )

    try:
        db.execute(
            delete(bakatPengguna)
            .where(
                bakatPengguna.c.idPengguna == id_pengguna,
                bakatPengguna.c.idBakat.in_(request.bakat_id)
            )
        )
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error menghapus bakat"
        )
    
    return {"message": "Bakat berhasil dihapus"}

@router.get("/all")
def ambil_semua_data_bakat(user: Annotated[dict, Depends(validate_token)],db: Session = Depends(get_db)):
    query = []
    try:
        query = db.execute(select(Bakat.idMinat,Bakat.nama)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error pada sambungan database"
        )
    data = []
    for q in query:
        data.append({"idBakat":q[0],"nama":q[1]})
    message = {"message":"sukses menerima data bakat","data":data}
    return message