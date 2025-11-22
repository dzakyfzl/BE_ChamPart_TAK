from fastapi import APIRouter, Response, status, Depends,File,UploadFile
from fastapi.responses import FileResponse
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import and_, insert, select, text, func, delete, update

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..auth.jwt_auth import create_token
from ..depedency import validate_token
import os
import shutil
import datetime

router = APIRouter(
    prefix="/file",
    tags=["File"]
)

@router.get("/get/{id}",status_code=200)
async def dapatkan_file(id:str,response:Response,user: Annotated[dict,Depends(validate_token)], db:Session = Depends(get_db)):
    query = None
    try:
        query = db.execute(select(Lampiran.nama, Lampiran.folder,Lampiran.jenis,Lampiran.ukuran).select_from(Lampiran).where(Lampiran.idLampiran==id)).first()
    except Exception as e:
        print("ERROR : ",e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "masalah pada sambungan database"}
    
    try:
        output =  FileResponse(path=query[1],media_type=query[2],headers={"Content-Disposition": "inline"},filename=query[0])
    except Exception as e:
        print("ERROR : ",e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "file rusak atau tidak ada"}
    
    return output


@router.post("/upload/account",status_code=200)
async def create_upload_file(user: Annotated[dict,Depends(validate_token)],response: Response,file: UploadFile, db:Session = Depends(get_db)):

    if not file:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"tidak ada file yang terbaca"}
    if file.content_type != "image/jpeg" and file.content_type != "image/png":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"messsage": "format salah, harap kirimkan foto yang benar"}
    
    query_exist = None
    try:
        if user["role"] == 'Pengguna':
            stmt = select(Pengguna.idLampiran).where(Pengguna.username==user["username"])
        elif user["role"] == 'AdminInstansi':
            stmt = select(AdminInstansi.idLampiran).where(AdminInstansi.username==user["username"])
        elif user["role"] == 'AdminPengawas':
            stmt = select(AdminPengawas.idLampiran).where(AdminPengawas.username==user["username"])
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"akun di role ini tidak ditemukan"}
        
        query_exist = db.execute(stmt).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if query_exist[0]:
        query_file_exist = db.execute(select(Lampiran.nama,Lampiran.folder).where(Lampiran.idLampiran==query_exist[0])).first()
        try:
            os.remove(path=query_file_exist[1])
        except Exception as e:
            print("ERROR : ",e)
            response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "error menghapus file"}
        try:
            if user["role"] == 'Pengguna':
                stmt = update(Pengguna).where(Pengguna.username==user["username"]).values(idLampiran=None)
            elif user["role"] == 'AdminInstansi':
                stmt = update(AdminInstansi).where(AdminInstansi.username==user["username"]).values(idLampiran=None)
            elif user["role"] == 'AdminPengawas':
                stmt = update(AdminPengawas).where(AdminPengawas.username==user["username"]).values(idLampiran=None)
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"message":"akun di role ini tidak ditemukan"}
            db.execute(stmt)
            db.execute(delete(Lampiran).where(Lampiran.idLampiran==query_exist[0]))
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
        
    
    file.filename = user["username"] + "_" + datetime.datetime.now().strftime("%Y-%m-%d[%H:%M:%S]")
    filepath = os.path.join("/media", file.filename)
    try:
        with open(filepath, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        print("ERROR : ",e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()

    
    query = None
    try:
        db.execute(insert(Lampiran).values(nama=file.filename,jenis=file.content_type,ukuran=file.size,folder=filepath))
        db.commit()
        query = db.execute(select(Lampiran.idLampiran).select_from(Lampiran).where(Lampiran.nama==file.filename)).first()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    try:
        if user["role"] == 'Pengguna':
            stmt = update(Pengguna).where(Pengguna.username==user["username"]).values(idLampiran=query[0])
        elif user["role"] == 'AdminInstansi':
            stmt = update(AdminInstansi).where(AdminInstansi.username==user["username"]).values(idLampiran=query[0])
        elif user["role"] == 'AdminPengawas':
            stmt = update(AdminPengawas).where(AdminPengawas.username==user["username"]).values(idLampiran=query[0])
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message":"akun di role ini tidak ditemukan"}

        query = db.execute(stmt)

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"messsage": "file berhasil dikirimkan"}

@router.post("/upload/instansi",status_code=200)
async def create_upload_file(user: Annotated[dict,Depends(validate_token)],response: Response,file: UploadFile, db:Session = Depends(get_db)):
    query = None
    query2 = None 
    
    if not file:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"tidak ada file yang terbaca"}
    if file.content_type != "image/jpeg" and file.content_type != "image/png":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"messsage": "format salah, harap kirimkan foto yang benar"}
    
    if user["role"] != 'AdminInstansi':
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda bukan admin instansi"}
    
    try:
        query = db.execute(select(AdminInstansi.idInstansi).where(AdminInstansi.username==user["username"])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if not query[0]:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda bukan admin instansi"}
    
    query_exist = None
    try:
        query_exist = db.execute(select(Instansi.idLampiran).where(Instansi.idInstansi==query[0])).first()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    if query_exist[0]:
        query_file_exist = db.execute(select(Lampiran.nama,Lampiran.folder).where(Lampiran.idLampiran==query_exist[0])).first()
        try:
            os.remove(path=query_file_exist[1])
        except Exception as e:
            print("ERROR : ",e)
            response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message": "error menghapus file"}
        try:
            db.execute(update(Instansi).where(Instansi.idInstansi==query[0]).values(idLampiran=None))
            db.execute(delete(Lampiran).where(Lampiran.idLampiran==query_exist[0]))
            db.commit()
        except Exception as e:
            print(f"ERROR : {e}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"message":"error pada sambungan database"}
    
    file.filename = str(query[0]) + "_INSTANSI_" + datetime.datetime.now().strftime("%Y-%m-%d[%H:%M:%S]")
    filepath = os.path.join("/media", file.filename)
    try:
        with open(filepath, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        print("ERROR : ",e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()

    
    try:
        db.execute(insert(Lampiran).values(nama=file.filename,jenis=file.content_type,ukuran=file.size,folder=filepath))
        db.commit()
        query2 = db.execute(select(Lampiran.idLampiran).select_from(Lampiran).where(Lampiran.nama==file.filename)).first()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    try:
        db.execute(update(Instansi).where(Instansi.idInstansi==query[0]).values(idLampiran=query2[0]))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"messsage": "file berhasil dikirimkan"}

@router.post("/upload/kegiatan",status_code=200)
async def create_upload_file(user: Annotated[dict,Depends(validate_token)],response: Response,file: UploadFile, db:Session = Depends(get_db)):
    query = None
    query2 = None 
    
    if not file:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message":"tidak ada file yang terbaca"}
    if file.content_type != "image/jpeg" and file.content_type != "image/png":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"messsage": "format salah, harap kirimkan foto yang benar"}
    
    if user["role"] != 'AdminInstansi':
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message":"anda bukan admin instansi"}
    
    
    file.filename = "KEGIATAN_" + datetime.datetime.now().strftime("%Y-%m-%d[%H:%M:%S]")
    filepath = os.path.join("/media", file.filename)
    try:
        with open(filepath, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        print("ERROR : ",e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()

    query2 = None
    try:
        db.execute(insert(Lampiran).values(nama=file.filename,jenis=file.content_type,ukuran=file.size,folder=filepath))
        db.commit()
        query2 = db.execute(select(Lampiran.idLampiran).select_from(Lampiran).where(Lampiran.nama==file.filename)).first()

    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}

    try:
        db.execute(update(Kegiatan).where(Kegiatan.idKegiatan==id).values(idLampiran=query2[0]))
        db.commit()
    except Exception as e:
        print(f"ERROR : {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message":"error pada sambungan database"}
    
    return {"messsage": "file berhasil dikirimkan","idLampiran":query2[0]}