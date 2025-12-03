import hashlib
import os
from fastapi import Depends, FastAPI
from typing import Annotated  
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, func
from .database.database import get_db, SessionLocal, Base, engine
from .database.models import * 
from .data.minatbakat import data_minat,data_bakat
from .depedency import validate_token
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from .routers import (
    account, 
    approve, 
    kegiatan, 
    minat,
    bakat,
    file,
    akunPengguna,
    akunAdminPengawas,
    akunAdminInstansi,
    instansi,
    calon,
    notification,
    simpan,
    token,
)

Base.metadata.create_all(bind=engine)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    count_m = []
    count_b = []
    
    try:
        count_m = db.execute(select(func.count("*")).select_from(Minat)).first()
        count_b = db.execute(select(func.count("*")).select_from(Bakat)).first()
        count_ap = db.execute(select(func.count("*")).select_from(AdminPengawas)).first()
    except Exception as e:
        print("ERROR : ", e)
    
    if count_m[0] == 0 and count_b[0] == 0:
        try:
            db.execute(insert(Minat).values(data_minat))
            db.execute(insert(Bakat).values(data_bakat))
            db.execute(insert(AdminPengawas).values(username="Admin",))
            db.commit()
        except Exception as e:
            print("ERROR : ", e)
    if count_ap[0] == 0:
        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
        salt = os.urandom(32).hex()
        prehash_password = ADMIN_PASSWORD + salt
        hashed_password = hashlib.sha256(prehash_password.encode('utf-8')).hexdigest()

        try:
            db.execute(insert(AdminPengawas).values(username=ADMIN_USERNAME,email=ADMIN_EMAIL,jabatan="Main Admin",salt=salt,hashed_password=hashed_password))
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
    yield
    print("app dimatikan")

app = FastAPI(lifespan=lifespan,docs_url='/docs',redoc_url='/redocs')

app.include_router(account.router)
app.include_router(akunAdminInstansi.router)
app.include_router(akunAdminPengawas.router)
app.include_router(akunPengguna.router)
app.include_router(instansi.router)
app.include_router(minat.router)
app.include_router(bakat.router)
app.include_router(calon.router)
app.include_router(approve.router)
app.include_router(kegiatan.router) 
app.include_router(file.router)
app.include_router(notification.router)
app.include_router(simpan.router)
app.include_router(token.router)