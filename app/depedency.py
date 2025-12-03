from email.utils import formatdate, make_msgid
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .database.database import get_db
from .database.models.refreshToken import RefreshToken
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
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp_server:
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
    user = {"username": "", "role": ""}
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload["type"] != "Access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user["username"] = payload['sub']
    user["role"] = payload["role"]
    
    
    return user

async def validate_ref_token(credentials: Annotated[str, Depends(security)],db: Session = Depends(get_db)):
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
    if payload["type"] != "Refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        stmt = select(RefreshToken.isi).select_from(RefreshToken).where(RefreshToken.username==payload["sub"])
        query_isExist = db.execute(stmt).first()
    except Exception as e:
        print("ERROR : ",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Masalah pada database",
        )
    if query_isExist == None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sesi telah berakhir, silahkan login terlebih dahulu",
        )
    if query_isExist[0] != token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sesi telah berakhir, silahkan login terlebih dahulu",
        )
    user["username"] = payload['sub']
    user["role"] = payload["role"]
    return user