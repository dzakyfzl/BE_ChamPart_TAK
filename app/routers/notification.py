from fastapi import APIRouter, Response, status, Depends, BackgroundTasks
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, text, func, delete, update
from sqlalchemy import Date, cast
from datetime import datetime, timedelta, timezone

from app.classmodel.Kegiatan import *
from app.depedency import send_email

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token, verify_cron_key

router = APIRouter(prefix="/notification", tags=["Notifikasi"])

@router.get("/trigger",status_code=200,dependencies=[Depends(verify_cron_key)])
async def pemicu_notifikasi_harian(response:Response,bc_tasks:BackgroundTasks,db: Session = Depends(get_db)):
    besok = datetime.now().date(timezone(timedelta(hours=7))) + timedelta(days=1)
    query = []
    try:
        stmt = (select(Kegiatan.nama,Pengguna.username,Pengguna.email)
                 .join(simpan,Kegiatan.idKegiatan==simpan.c.idKegiatan)
                 .join(Pengguna,Pengguna.idPengguna==simpan.c.idPengguna)
                 .where(cast(Kegiatan.waktu,Date) == besok))
        db.execute(stmt).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    if not query:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message":"tidak ada user"}
    for q in query:
        isi = f"Hai, {q[1]}!\n\nMengingatkan bahwa kegiatan {q[0]} dilaksanakan 1 hari lagi\nJangan Lupa Yaa... :)"
        bc_tasks.add_task(send_email,subject=f"CHAMPART - 1 Hari Lagi {q[0]}",body=isi,recipients=q[2])
    return {"message":"trigger notifikasi telah terlaksana"}

@router.get("/test-email",status_code=200,dependencies=[Depends(verify_cron_key)])
async def pemicu_notifikasi_harian(response:Response,bc_tasks:BackgroundTasks,db: Session = Depends(get_db)):
    query = []
    try:
        query = db.execute(select(AdminInstansi.email,AdminInstansi.username)).all()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    for q in query:
        isi = f"Hai, {q[1]}!"
        bc_tasks.add_task(send_email,subject=f"CHAMPART - Test mail for {q[0]}",body=isi,recipients=q[0])
    return {"message":"trigger test notifikasi telah terlaksana"}