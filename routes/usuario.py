from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data.models import Usuario,SessionLocal,Loja


usuario_router = APIRouter(prefix="/usuario", tags=["usuario"])


class usuarioCreate(BaseModel):
    IdLoja : int
    LOGIN : str
    SENHA : str
    CARGO: str

@usuario_router.post("/")
def criar_usuarios(usuario:usuarioCreate):
    db: Session = SessionLocal()

    novo =  Usuario(
        IdLoja = usuario.IdLoja,
        LOGIN = usuario.LOGIN,
        SENHA = usuario.SENHA,
        CARGO = usuario.CARGO
    )

    db. add(novo)
    db.commit()
    db.refresh(novo)

    return novo