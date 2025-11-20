from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.database import get_db

from ..database.models import * 
from ..classmodel import *

from ..depedency import validate_token

router = APIRouter(prefix="/kegiatan", tags=["Kegiatan"])

@router.get("/", response_model=List[JSONKegiatanResponse])
def get_all_kegiatan(
    user: Annotated[dict, Depends(validate_token)],  
    db: Session = Depends(get_db)
):
    Kegiatan_list = db.query(Kegiatan).all()
    if not Kegiatan_list:
        return []

    return Kegiatan_list