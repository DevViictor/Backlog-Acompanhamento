from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data.models import SessionLocal, Usuario
import bcrypt

auth_router =  APIRouter(prefix="/login",tags=["auth"])

class LoginShema(BaseModel):
    LOGIN: str
    SENHA: str

@auth_router.post("/")
def login(dados:LoginShema):
    db = SessionLocal()

    try:
        usuario_db = db.query(Usuario).filter(Usuario.LOGIN == dados.LOGIN).first()

        if not usuario_db:
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

        senha_hash = dados.SENHA.encode("utf-8")

        hash_banco = usuario_db.SENHA.encode("utf-8")
        
        if not bcrypt.checkpw(senha_hash,hash_banco):
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

        return {
            "status": "sucesso",
            "id": usuario_db.ID,
            "usuario": usuario_db.LOGIN,
            "cargo": usuario_db.CARGO,
            "loja_id": usuario_db.IdLoja
        }

    finally:
        db.close()