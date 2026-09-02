import streamlit as st
from fastapi import FastAPI
from passlib.context import CryptContext
import os 
from dotenv import load_dotenv
from routes.loja import loja_router
from routes.usuario import usuario_router
from routes.consultor import consultor_router
from routes.auth.login import auth_router
from routes.cadastro_backlog import cadastro_router

load_dotenv()

SECRETY_KEY = os.getenv("SECRETY_KEY")

bcrypt_context =  CryptContext(schemes=["bcrypt"],deprecated = "auto")

app =  FastAPI()

app.include_router(loja_router)
app.include_router(usuario_router)
app.include_router(consultor_router)
app.include_router(auth_router)
app.include_router(cadastro_router)
