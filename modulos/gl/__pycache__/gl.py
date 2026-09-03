import streamlit as st 
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

def acompanhamento_geral():

    st.set_page_config(page_title="",page_icon="",layout="wide")

    colored_header(
        label="Acompanhamento Backlog",
        description= "Seu relatório de acompanhamento",
        color_name="violet-70"
    )

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1:

        colored_header(
            label= "Total",
            description= "Total de fibras",
            color_name= "violet-70"
        )

        TotalBackalog = st.metric(
                label="",
                value=0
            )
    
    with col2:

        colored_header(
            label= "Instaladas",
            description= "Fibras instaladas",
            color_name="green-70"
        )

        instaladas = st.metric(
            label="",
            value=0
        )

    with col3:

        colored_header(
            label= "Agendadas",
            description= "Fibras agendadas",
            color_name="yellow-80"
        )

        agendadas = st.metric(
            label="",
            value=0
        )

    with col4:

        colored_header(
            label= "Pendentes",
            description= "Fibras pendentes (instalação/agendamento)",
            color_name="orange-70"
        )

        pendentes = st.metric(
            label="",
            value=0
        )

        style_metric_cards(
            background_color="",
            border_color="#00C8FF"
        )


    with col5:
        
        colored_header(
            label= "Canceladas",
            description="Fibras canceladas",
            color_name="red-70"
        )

        canceladas = st.metric(
            label="",
            value=0
        )


    consultores = []

    with st.sidebar:

        filtro = st.selectbox("Filtro",consultores)
        
        data = st.date_input("Data")

def acompanhamento_diario():

    st.set_page_config(page_title="",page_icon="",layout="wide")

    colored_header(
        label="Backlog Diário",
        description= "Fibras agendadas ",
        color_name="violet-70"
    )


    with st.sidebar:
        data =  st.date_input("Data")
    


def controle_tela_gl(id_loja=None):

    with st.sidebar:
         
        menu_gl = option_menu(

            "Menu",
            ["Acompanhamento diário","Relatorio geral"],
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


    if menu_gl == "Acompanhamento diário":
        acompanhamento_diario()

    elif menu_gl == "Relatorio geral":
        acompanhamento_geral()