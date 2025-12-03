from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from ..database.database import get_db
from ..database.models import *
from ..classmodel import *
from ..depedency import validate_ref_token, validate_token
from ..auth.jwt_auth import *

router = APIRouter(prefix="/token", tags=["Pertokenan"])

@router.get("/access/validate", status_code=200)
def verifikasi_access_token(user: Annotated[dict, Depends(validate_token)]):
    return {"message": "Yahhoo~! token-mu valid", "user": user}

@router.get("/access/get", status_code=200)
def verifikasi_refresh_token(user: Annotated[dict, Depends(validate_ref_token)]):
    access_token = create_refresh_token(user["username"],user["role"])
    return {"message": "Yahhoo~! token-mu valid", "user": user,"access_token":access_token}