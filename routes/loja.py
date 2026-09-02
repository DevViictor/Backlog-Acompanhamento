from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data.models import Loja,SessionLocal

loja_router = APIRouter(prefix="/loja", tags=["loja"])

class LojaC(BaseModel):
    loja : str

@loja_router.post("/")
def adicionar_loja(loja:LojaC):

    db: Session = SessionLocal()

    novo = Loja(
        nome = loja.loja
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()

    return novo

@loja_router.get("/")
def lista_lojas():

    try:
        db = SessionLocal()

        lojas = db.query(Loja).all()

        return [{"id": loja.ID,"nome":loja.nome} for loja in lojas]
    finally:
        db.close()
