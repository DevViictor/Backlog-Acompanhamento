from pages.adm.cadastro import tela_cadastro
from pages.gl.gl import controle_tela_gl
from pages.consultor.consultor import tela_consultor
from pages.analista.produto_oferta import controle_tela_analista
import streamlit as st
import os
from dotenv import load_dotenv
import requests



load_dotenv()

API_URL = st.secrets["API_URL"]



if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "loja_id" not in st.session_state:
    st.session_state["loja_id"] = None

if "tela" not in st.session_state:
    st.session_state["tela"] = "login"

def realizar_logout():
    
    st.session_state.clear()
    st.session_state["tela"] = "login"
    st.rerun()

def exibir_sidebar_usuario():
    """Exibe informações do usuário logado e o botão de logout no sidebar."""
    usuario = st.session_state.get("usuario_logado")
    if usuario and st.session_state["tela"] != "login":
        with st.sidebar:
            
            if st.button(
                "🚪 Sair",
                type="secondary",
                use_container_width=True,
                key="btn_logout",
            ):
                realizar_logout()
        
def carregar_login():

    st.set_page_config(page_title="Login", page_icon="", layout="centered")

    st.title("Login")

    usuario = st.text_input("Usuario",key="login_usuario")
    senha = st.text_input("Senha",type="password",key="login_senha")

    if st.button("Login"):

        if not usuario or not senha:
            st.warning("Preencha os campos obrigatórios")
            return
        
        payload = {"LOGIN": usuario, "SENHA":senha}

        try:
            res = requests.post(f"{API_URL}/login/",json=payload)

            if res.status_code == 200:
                dados = res.json()
                st.session_state["usuario_logado"] = dados
                st.session_state["loja_id"] = dados.get("loja_id")
                cargo = dados.get("cargo")

                if cargo == "ADM":
                    st.session_state["tela"]= "cadastro"

                elif cargo == "GL":
                    st.session_state["tela"] = "painel_gl"

                elif cargo == "Consultor":
                    st.session_state["tela"] = "painel_consultor"

                elif cargo == "ANALISTA":
                    st.session_state["tela"] = "tela_analista"

                st.rerun()

                st.success("Login realizado!")

            else:

                try:
                    detalhes = res.json()
                except Exception:
                    detalhes = res.text

                st.error(f"Usuário ou senha inválidos.")
        except requests.exceptions.ConnectionError:
            st.error(f"Erro ao conectar à API FastAPI:.")

        


if st.session_state["tela"] == "login":
    carregar_login()

elif st.session_state["tela"] == "painel_gl":
    controle_tela_gl()

elif st.session_state["tela"] == "cadastro":
    tela_cadastro()

elif st.session_state["tela"] == "painel_consultor":
    tela_consultor()

elif st.session_state["tela"] == "tela_analista":
    controle_tela_analista()

exibir_sidebar_usuario()