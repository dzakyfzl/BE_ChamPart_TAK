from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .database.database import get_db
from .database.models.pengguna import Pengguna
from .database.models.adminPengawas import AdminPengawas
from .database.models.adminInstansi import AdminInstansi
from .auth.jwt_auth import decode_token

security = HTTPBearer()


async def validate_token(credentials: Annotated[str, Depends(security)],db: Session = Depends(get_db)) -> dict:
    token = credentials.credentials  # Ambil token dari credentials
    payload = decode_token(token)
    query_isExist = None
    user = {"username": "", "role": ""}

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        if payload["role"] == "Pengguna":
            query_isExist = db.execute(select(func.count('*')).select_from(Pengguna).where(Pengguna.username==payload['sub'])).all()
        elif payload["role"] == "AdminPengawas":
            query_isExist = db.execute(select(func.count('*')).select_from(AdminPengawas).where(AdminPengawas.username==payload['sub'])).all()
        elif payload["role"] == "AdminInstansi":
            query_isExist = db.execute(select(func.count('*')).select_from(AdminInstansi).where(AdminInstansi.username==payload['sub'])).all()
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
    user["username"] = payload['sub']
    user["role"] = payload["role"]
    
    
    return user