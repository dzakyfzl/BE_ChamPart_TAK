import time
from datetime import datetime, timedelta, timezone
from authlib.jose import jwt, JoseError
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("TOKEN_SECRET_KEY")
ALGORITHM = "HS256"  # Algoritma signing
ACCESS_TOKEN_EXPIRE_DAYS = 1


def create_jwt(username: str) -> str:
    """
        Membuat JWT Token
    """


    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    

    payload = {
        "sub": username,  
        "iat": int(time.time()),      
        "exp": int(expire.timestamp()) 
    }
    header = {"alg": ALGORITHM}
    try:
        token = jwt.encode(header, payload, SECRET_KEY)
        return token.decode('utf-8')
    except JoseError as e:
        print(f"Error encoding token: {e}")
        return None


def decode_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY)
        
        return payload
    
    except JoseError as e:
        print(f"Token invalid: {e}")
        return None