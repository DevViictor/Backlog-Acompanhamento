from sqlalchemy import create_engine,String,Integer,ForeignKey,Date,Column,Time,Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

db =  create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=db
)

backlog = declarative_base()

class Loja(backlog):
    __tablename__ = "loja"

    ID = Column ("ID",Integer,primary_key=True,autoincrement=True,nullable=False)
    nome = Column ("NOME",String,nullable=False)

class Usuario(backlog):
    __tablename__ = "usuario"

    ID = Column ("ID",Integer,primary_key=True,autoincrement=True,nullable=False)
    IdLoja = Column ("IdLoja",Integer,ForeignKey("loja.ID"),nullable=False)
    LOGIN = Column ("LOGIN",String,nullable=False)
    SENHA = Column ("SENHA",String,nullable=False)
    CARGO = Column ("CARGO",String,nullable=False)
    
class Consultor(backlog):
    __tablename__ = "consultor"
    
    ID = Column ("ID",Integer,primary_key=True,autoincrement=True,nullable=False)
    IdLoja = Column ("IdLoja",ForeignKey("loja.ID"),nullable=False)
    NOME =  Column ("NOME",String,nullable=False)

class CadastroBacklog(backlog):
    __tablename__ = "cadastro_backlog"

    ID =  Column ("ID",Integer,primary_key=True,autoincrement=True,nullable=False)
    IdLoja =  Column ("IdLoja",Integer,ForeignKey("loja.ID"),nullable=False)
    IdConsultor = Column ("IdConsultor",Integer,ForeignKey("consultor.ID"),nullable=False)
    ORDEM = Column ("ORDEM",String,nullable=False)
    CRIACAO = Column ("CRIACAO",String,nullable=False)
    INSTALACAO = Column ("INSTALACAO",String,nullable=False)
    HORA = Column("HORA",String,nullable=False)
    STATUS =  Column ("STATUS",String,nullable=False)
    OBSERVACAO = Column("OBSERVACAO",String,nullable=True,server_default="Sem observação")

class Analista(backlog):
    __tablename__ = "analista"

    ID = Column ("ID",Integer,primary_key=True,autoincrement=True,nullable=False)
    IdLoja = Column ("IdLoja",Integer,ForeignKey("loja.ID"),nullable=False)
    NOME = Column ("NOME",String,nullable=False)

class Ofertas(backlog):
    __tablename__ = "ofertas"

    ID = Column ("ID",Integer,primary_key=True,autoincrement=True,nullable=False)
    IdLoja = Column ("IdLoja",Integer,ForeignKey("loja.ID")) 
    PRODUTO = Column ("PRODUTO",String,nullable=False)
    PRECO =  Column ("PRECO",Float,nullable=False)

class Esperados(backlog):
    __tablename__ = "esperados"

    ID =  Column ("ID",Integer,primary_key =True,autoincrement=True,nullable=False)
    IdLoja = Column ("IdLoja",Integer,ForeignKey("loja.ID"),nullable=False)
    PRODUTO = Column ("PRODUTO",String,nullable=False)
    QUANTIDADE = Column ("QUANTIDADE",Integer,nullable=False)
           
class Acompanhamento(backlog):
    __tablename__ = "acompanhamento"

    ID = Column ("ID",Integer,primary_key=True,autoincrement=True)
    IdLoja = Column ("IdLoja",Integer,ForeignKey("loja.ID"),nullable=False)
    IdConsultor =  Column ("IdConsultor",Integer,ForeignKey("consultor.ID"),nullable=False)
    IdBacklog = Column ("IdBacklog",Integer,ForeignKey("cadastro_backlog.ID"),nullable=False)
    DATA = Column ("DATA",String,nullable=False)

