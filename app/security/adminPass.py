from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

SECRET_KEY = os.getenv("TOKEN_SECRET_KEY")

# Generate kunci unik untuk pendaftaran akun & instansi
def generate_pass(unique:str,email:str, nama_instansi:str) -> str:
    passkey = unique + email + nama_instansi + SECRET_KEY
    return hashlib.sha256(passkey.encode('utf-8')).hexdigest()

def verif_pass(unique:str, email:str, nama_instansi:str, existed_passkey:str) -> bool:
    passkey = unique + email + nama_instansi + SECRET_KEY
    passkey = hashlib.sha256(passkey.encode('utf-8')).hexdigest()
    if existed_passkey == passkey:
        return True
    else:
        return False