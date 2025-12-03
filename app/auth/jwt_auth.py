import time
from datetime import datetime, timedelta, timezone
from authlib.jose import jwt, JoseError
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("TOKEN_SECRET_KEY")
ALGORITHM = "HS256"  # Algoritma signing
ACCESS_TOKEN_EXPIRE_MINUTE = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


def create_token(username: str, role: str) -> str:
    """
        Membuat JWT Token
    """


    expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTE))
    

    payload = {
        "sub": username,  
        "iat": int(time.time()),      
        "exp": int(expire.timestamp()),
        "role":role,
        "type":"Access"
    }
    header = {"alg": ALGORITHM}
    try:
        token = jwt.encode(header, payload, SECRET_KEY)
        return token.decode('utf-8')
    except JoseError as e:
        return "Error"


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY)
        
        return payload
    
    except JoseError as e:
        return None
    
def create_refresh_token(username:str,role:str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    

    payload = {
        "sub": username,  
        "iat": int(time.time()),      
        "exp": int(expire.timestamp()),
        "role":role,
        "type":"Refresh"
    }
    header = {"alg": ALGORITHM}
    try:
        token = jwt.encode(header, payload, SECRET_KEY)
        return token.decode('utf-8')
    except JoseError as e:
        print("ERROR : ",e)
        return "Error"