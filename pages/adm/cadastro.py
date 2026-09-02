import streamlit as st
from streamlit_extras.colored_header import colored_header
import bcrypt
from streamlit_option_menu import option_menu 
import os 
from dotenv import load_dotenv
import requests


load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(page_title="Cadastros",page_icon="")

@st.cache_data(ttl=60)
def buscar_lojas():
    try:
        res = requests.get(f"{API_URL}/loja/")
        if res.status_code == 200:
            return res.json() 
    except Exception:
        pass
    return []

def cadastro_usuario():

    colored_header(

        label = "Cadastros",
        description= "Cadastros de usuários",
        color_name="blue-70"
    )
    
    usuario = st.text_input("Usuario",key="cadastro_usuarios")

    senha = st.text_input("senha",key="cadastro_senha",type="password") 

    lojas = buscar_lojas()

    if not lojas:
        st.warning("Nenhuma loja encontrada! Cadastre uma loja primeiro.")
        return

    mapa_lojas = {item["nome"]: item["id"] for item in lojas}

    loja = st.selectbox("Loja",options=list(mapa_lojas.keys()))

    cargos = ["","GL","Consultor","ANALISTA"]
    
    cargo = st.selectbox("Cargo",cargos)

    if st.button("Cadastrar"):

        if not usuario or not senha or not loja or not cargo:
            st.warning("Por favor, preencha todos os campos obrigatorios.")
            return

        senha_cripito = senha.encode("utf-8")
        salt = bcrypt.gensalt()
        senha_hashed = bcrypt.hashpw(senha_cripito, salt).decode("utf-8")
        loja_id = mapa_lojas[loja]

        payload ={
            "IdLoja": loja_id,
            "LOGIN" : usuario,
            "SENHA" : senha_hashed,
            "CARGO" : cargo
        }

        try:
            res = requests.post(f"{API_URL}/usuario/",json=payload)

            if res.status_code == 200:
                st.success(f"Usuario cadastrado!")

            else:
                st.error(f"Error ao cadastrar na API:{res.text}")
        except requests.exceptions.ConnectionError:
            
            st.error("Erro de conexão com a API")


def cadastro_loja():

    colored_header(
    
            label = "Cadastros",
            description= "Cadastros de loja",
            color_name="blue-70"
        )

    loja = st.text_input("Digite o nome da loja")
    
    if st.button("Cadastrar"):

        payload = {"loja": loja}

        try:
                
                response = requests.post(f"{API_URL}/loja/", json=payload)

                if response.status_code == 200:
                    dados_resposta = response.json()
                    st.success(f"Loja '{dados_resposta.get('nome')}' cadastrada com sucesso!)")
                    
                else:
                    st.error(f"Erro ao salvar na API. Status: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Verifique se o FastAPI está em execução.")


def cadastro_consultores():

    nome = st.text_input("Nome do consultor")

    lojas = buscar_lojas()
    
    if not lojas:
            st.warning("Nenhuma loja encontrada! Cadastre uma loja primeiro.")
            return
    
    mapa_lojas = {item["nome"]: item["id"] for item in lojas}

    loja = st.selectbox("Loja",options=list(mapa_lojas.keys()))

    if st.button("Cadastrar"):

        loja_id = mapa_lojas[loja]

        payload ={
            "IdLoja": loja_id,
            "NOME" : nome,
        }

        response = requests.post(f"{API_URL}/consultor/", json=payload)

        try:
                if response.status_code == 200:
                    dados_resposta = response.json()
                    st.success(f"Consultor cadastrado com sucesso!)")
                    
                else:
                    st.error(f"Erro ao salvar na API. Status: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Verifique se o FastAPI está em execução.")


        

def tela_cadastro():
    
    with st.sidebar:
            
        menu_cadastro= option_menu(
            "Menu",
            ["Cadastro"],
            icons=["house-door"],
            default_index=0,
            styles={
                "container": {
                    "background-color": "#000000ff",
                },
                "nav-link-selected":{
                    "background-color": "#008000"
                }
            }
        )

    if menu_cadastro == "Cadastro":

        colored_header(

        label= "Cadastro",
        description= "Cadastro de informações",
        color_name="violet-70"
        )
        
        sub_menu_cadastro = option_menu(
            menu_title=None,
            options=["Cadastro de login","Cadastro de loja","Cadastro de consultor"],
            icons=["box-arrow-in-right","lock","person"],
            orientation="horizontal",
            styles={
                "nav-link-selected":{
                    "background-color": "#008000"
                }
            }
        )

        if sub_menu_cadastro == "Cadastro de login":
            cadastro_usuario()


        elif sub_menu_cadastro == "Cadastro de loja":
            cadastro_loja()

        elif sub_menu_cadastro == "Cadastro de consultor":
            cadastro_consultores()