import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu

def cadastro_produtos():

    st.set_page_config(page_title="Cadastro de produtos e ofertas",layout="centered")

    colored_header(
        label="Produtos esperados",
        description="Cadastro dos produtos esperados",
        color_name="violet-70"
    )

    nome = st.text_input("Nome do produto")

    quantiade = st.text_input("Quantidade do produto")

    if st.button("Cadastrar"):
        pass

        
def atualizar_produtos():

    st.set_page_config(page_title="Cadastro de produtos e ofertas",layout="centered")

    colored_header(
        label="Atualização dos produtos",
        description="Atualização do nome e quantidade dos produtos",
        color_name="violet-70"
    )

    nome = st.text_input("Nome do produto com desconto")
    
    quantiade = st.text_input("Valor do produto em oferta")

    if st.button("Cadastrar"):
        
        pass



def cadastrar_ofertas():

    colored_header(
            label="Ofertas",
            description="Cadastro dos produtos esperados",
            color_name="violet-70"
        )
    
    nome = st.text_input("Nome do produto")

    quantiade = st.text_input("valor da oferta: ")

    if st.button("Cadastrar"):
        pass


def controle_tela_analista():

    with st.sidebar:
                
        menu_cadastro= option_menu(
            "Menu",
            ["Produtos","Ofertas"],
            icons=["bag","tag"],
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
    
    if menu_cadastro == "Produtos":
        
        sub_menu_cadastro = option_menu(
            menu_title=None,
            options=["Cadastro de produtos","Atualizar produtos"],
            icons=["box-arrow-in-right","lock","person"],
            orientation="horizontal",
            styles={
                "nav-link-selected":{
                    "background-color": "#008000"
                }
            }
        )

        if sub_menu_cadastro == "Cadastro de produtos":
            cadastro_produtos()


        elif sub_menu_cadastro == "Atualizar produtos":
            atualizar_produtos()

        