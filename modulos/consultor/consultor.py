import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
import requests
import os 
from dotenv import load_dotenv


API_URL = st.secrets["API_URL"]

@st.cache_data(ttl=60)
def buscar_lojas():

    try:
        res = requests.get(f"{API_URL}/loja/")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=60)
def buscar_consultores(loja_id=None):
    params = {}
    if loja_id:
        params["loja_id"] = loja_id

    try:
        res = requests.get(
            f"{API_URL}/consultor/", params=params, timeout=5
        )
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

def Iguatemi_backlog_cadastro():

    usuario = st.session_state.get("usuario_logado", {})
    cargo = usuario.get("cargo")
    loja_id_sessao = st.session_state.get("loja_id")

    st.set_page_config(page_title="",page_icon="",layout="wide")

    colored_header(
        label= "Cadastro Fibra",
        description="Coloque as informações sobre a instalação",
        color_name="violet-70"
    )

    lojas = buscar_lojas()

    if not lojas:
        st.error("Nenhuma loja encontrada na API")

    mapa_lojas = {
        item.get("nome", item.get("NOME")): item.get("id", item.get("ID"))
        for item in lojas
    }

    # Lógica de Permissão / Multi-tenant para Seleção da Loja
    id_loja = None

    if cargo != "ADM" and loja_id_sessao:
        # Usuário não-ADM fica restrito à sua própria loja
        id_loja = loja_id_sessao
        # Encontra o nome da loja vinculada ao ID para exibição
        nome_loja = next(
            (k for k, v in mapa_lojas.items() if v == id_loja), "Sua Loja"
        )
        st.info(f"📍 **Loja ativa:** {nome_loja}")
    else:
        # Administrador pode escolher qualquer loja
        op_loja = ["Selecione a loja"] + list(mapa_lojas.keys())
        loja_selecionada = st.selectbox("Selecione a loja", options=op_loja)

        if loja_selecionada == "Selecione a loja":
            st.warning("Selecione uma loja para prosseguir.")
            return

        id_loja = mapa_lojas[loja_selecionada]
    
    consultores = buscar_consultores(id_loja)

    if not consultores:
            st.warning("Nenhum consultor encontrado!")
            return

    mapa_consultores = {
        item.get("nome", item.get("NOME")): item.get("id", item.get("ID"))
                for item in consultores
    }

    nome_consultor = st.selectbox("Nome do Consultor: ",options=list(mapa_consultores.keys()),key=f"select_consultor_{id_loja}",)

    id_consultor = mapa_consultores.get(nome_consultor)

    data_criacao = st.date_input("Data de criação: ")
    
    ordem = st.text_input("N° da ordem: ")

    data_instalacao = st.date_input("Data de instalação:")

    hora_instalacao = st.time_input("Horario de instalação:")

    status = "AGENDADA"

    if st.button("Cadastrar"):

        if not ordem:
            st.warning("Por favor, informe o número da ordem!")
            return

        payload =  {
           "Idloja" : id_loja,
           "IdConsultor": id_consultor,
           "CRIACAO": str(data_criacao),
           "ORDEM": ordem,
           "INSTALACAO": str(data_instalacao),
           "HORA": str(hora_instalacao),
           "STATUS": status
        }

        try:
            res = requests.post(f"{API_URL}/cadastro/",json=payload)
            if res.status_code == 200:
                st.success("Agendamento cadastrado!")
            else:
                st.error(f"Erro ao cadastrar: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Verifique a conexão")

def visualizar_produtos_iguatemi():

    st.set_page_config(page_title="",page_icon="",layout="wide")

    colored_header(
        label="Produtos",
        description="Produtos mais aguardados",
        color_name="violet-70"
    )

    col1,col2,col3 = st.columns(3)

    with col1:
        cardP1 =st.metric("17 PRO MAX",value=0)
        cardP2 =st.metric("S25 FE",value=0)
    with col2:
        cardP3 = st.metric("S26 ULTRA 512",value=0)
        cardP4 = st.metric("17 PRO",value=0)
    
    with col3:
        cardP5 = st.metric("PS5 SLIM DISK",value=0)
        cardP6 = st.metric("PS5 DIGITAL",value=0)

    colored_header(
        label="Ofertas",
        description="Produtos em ofertas",
        color_name="violet-70"
    )

    col1,col2,col3 = st.columns(3)

    with col1:
        cardO1 =st.metric("17 PRO MAX",value="R$")
        cardO2 =st.metric("S25 FE",value="R$")
    with col2:
        cardO3 = st.metric("S26 ULTRA 512",value="R$")
        cardO4 = st.metric("17 PRO",value="R$")
    
    with col3:
        cardO5 = st.metric("PS5 SLIM DISK",value="R$")
        cardO6 = st.metric("PS5 DIGITAL",value="R$")

    style_metric_cards(
        background_color="",
        border_color="#00C8FF"
    )

def tela_consultor():
    with st.sidebar:
        menu_consultor =  option_menu(

            "Menu",
            ["Cadastro Backlog"],
            menu_icon="house",
            icons=[""],
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

    if menu_consultor == "Cadastro Backlog":
        Iguatemi_backlog_cadastro()
