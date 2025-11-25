from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .database.database import get_db
from .database.models.pengguna import Pengguna
from .database.models.adminPengawas import AdminPengawas
from .database.models.adminInstansi import AdminInstansi
from .auth.jwt_auth import decode_token
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

security = HTTPBearer()

load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(subject, body, recipients):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = ', '.join(recipients)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
           smtp_server.login(EMAIL, EMAIL_PASSWORD)
           smtp_server.sendmail(EMAIL, recipients, msg.as_string())
    except Exception as e:
        print("ERROR: ",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengirimkan email",
        )
        
    
CRON_SECRET_KEY = os.getenv("CRON_SECRET_KEY")

async def verify_cron_key(x_cron_key: str = Header(..., alias="X-Cron-Key")):
    if x_cron_key != CRON_SECRET_KEY:
        raise HTTPException(status_code=401, detail="maaf layanan ini tidak dapat diakses")

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