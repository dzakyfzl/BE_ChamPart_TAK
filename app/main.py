from fastapi import Depends, FastAPI
from typing import Annotated  
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, func
from .database.database import get_db, SessionLocal, Base, engine
from .database.models import * 
from .data.minatbakat import minat, bakat
from .depedency import validate_token
from contextlib import asynccontextmanager
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
)

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    count_m = []
    count_b = []
    
    try:
        count_m = db.execute(select(func.count("*")).select_from(Minat)).first()
        count_b = db.execute(select(func.count("*")).select_from(Bakat)).first()
    except Exception as e:
        print("ERROR : ", e)
    
    if count_m[0] == 0 and count_b[0] == 0:
        try:
            db.execute(insert(Minat).values(minat))
            db.execute(insert(Bakat).values(minat))
            db.commit()
        except Exception as e:
            print("ERROR : ", e)
    yield
    print("app dimatikan")

app = FastAPI(lifespan=lifespan)

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


@app.get("/", status_code=200,tags=["Verify Token"])
def verifikasi_token(user: Annotated[dict, Depends(validate_token)]):
    return {"message": "Yahhoo~! token-mu valid", "user": user}
