from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data.models import SessionLocal, Consultor

consultor_router = APIRouter( prefix="/consultor", tags=["consultor"])

class ConsultorC(BaseModel):
    IdLoja:int
    NOME: str

@consultor_router.post("/")
def cadastro_consultor(consultor:ConsultorC):
    db: Session = SessionLocal()

    novo = Consultor(
        IdLoja = consultor.IdLoja,
        NOME = consultor.NOME
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()
    return novo

@consultor_router.get("/")
def lista_consultores(loja_id: Optional[int] = None):

    db: Session = SessionLocal()
    try:
        query = db.query(Consultor)

        
        if loja_id is not None:
            query = query.filter(Consultor.IdLoja == loja_id)

        consultores = query.all()

        return [
            {"id": consultor.ID, "nome": consultor.NOME}
            for consultor in consultores
        ]
    finally:
        db.close()