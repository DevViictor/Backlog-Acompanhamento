from fastapi import APIRouter,Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data.models import SessionLocal, CadastroBacklog,Consultor
from typing import List,Optional

cadastro_router =  APIRouter(prefix= "/cadastro", tags=["cadastro"])


class cadastroCreate(BaseModel):
    Idloja: int
    IdConsultor: int
    ORDEM: str
    CRIACAO: str
    INSTALACAO: str
    HORA: str
    STATUS: str

@cadastro_router.post("/")
def cadastro_backlog(cadastro:cadastroCreate):
    db: Session = SessionLocal()
    novo =  CadastroBacklog(
        IdLoja = cadastro.Idloja,
        IdConsultor = cadastro.IdConsultor,
        ORDEM = cadastro.ORDEM,
        CRIACAO = cadastro.CRIACAO,
        INSTALACAO = cadastro.INSTALACAO,
        HORA = cadastro.HORA,
        STATUS = cadastro.STATUS
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close
    return novo

@cadastro_router.get("/")
def lista_backlog(
    loja_id: Optional[int] = Query(
        None, description="ID da loja para filtragem"
    ),
    ):
        db: Session = SessionLocal()

        try:
            query = db.query(
                CadastroBacklog.ID,
                CadastroBacklog.IdLoja,
                Consultor.NOME.label("Consultor"),
                CadastroBacklog.CRIACAO,
                CadastroBacklog.ORDEM,
                CadastroBacklog.INSTALACAO,
                CadastroBacklog.HORA,
                CadastroBacklog.STATUS,
                CadastroBacklog.OBSERVACAO,
            ).join(Consultor, CadastroBacklog.IdConsultor == Consultor.ID)

            if loja_id is not None:
                query = query.filter(CadastroBacklog.IdLoja == (loja_id))

            resultados = query.all()
            return [dict(row._mapping) for row in resultados]

        finally:
            db.close()

class StatusUpdate(BaseModel):
    ID:int
    STATUS: str
    OBSERVACAO: Optional[str] = "Sem observação"


@cadastro_router.post("/atualizar-status")
def atualizar_status(itens: List[StatusUpdate]):
    db: Session = SessionLocal()
    atualizados = 0

    try:
        for item in itens:
            registro = (
                db.query(CadastroBacklog)
                .filter(CadastroBacklog.ID == item.ID)
                .first()
            )

            if registro:
                registro.STATUS = item.STATUS
                registro.OBSERVACAO = item.OBSERVACAO
                atualizados += 1

        db.commit()
        return {
            "status": "sucesso",
            "mensagem": f"{atualizados} registro(s) atualizado(s).",
        }
    except Exception as e:
        db.rollback()
    finally:
        db.close()
