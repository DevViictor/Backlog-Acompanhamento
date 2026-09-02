import os
import re
import urllib.parse
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

load_dotenv()

API_URL = st.secrets["API_URL"]
URL_API = st.secrets["URL_API"]


@st.cache_data(ttl=30)
def buscar_backlog_api(loja_id=None):
    params = {}
    if loja_id:
        params["loja_id"] = loja_id

    try:
        res = requests.get(f"{API_URL}/cadastro/", params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Erro ao carregar dados: {res.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o servidor: {e}")
        return []


def acompanhamento_geral():
    usuario = st.session_state.get("usuario_logado", {})
    cargo = usuario.get("cargo")
    loja_id_sessao = st.session_state.get("loja_id")

    loja_filtro = None if cargo == "ADM" else loja_id_sessao

    dados = buscar_backlog_api(loja_id=loja_filtro)

    if not dados:
        st.info("Nenhum registro encontrado para esta loja.")
        return

    @st.cache_data(ttl=60)
    def buscar_consultores():
        try:
            res = requests.get(f"{API_URL}/consultor/")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    colored_header(
        label="Acompanhamento Backlog",
        description="Seu relatório de acompanhamento",
        color_name="violet-70",
    )

    df_filtrado = pd.DataFrame(dados)

    consultores = buscar_consultores()

    if not consultores:
        st.warning("Nenhum consultor encontrado")
        return

    mapa_consultores = {
        item.get("nome", item.get("NOME")): item.get("id", item.get("ID"))
        for item in consultores
    }

    df_filtrado["CRIACAO"] = pd.to_datetime(
        df_filtrado["CRIACAO"], errors="coerce"
    )

    status_op = [
        "INSTALADO",
        "PENDENTE(AGENDAMENTO)",
        "PENDENTE(RETENÇÃO/ENRIQUECIMENTO)",
        "CANCELADO",
    ]

    with st.sidebar:
        filtro = st.selectbox(
            "Filtro", options=["Todos"] + list(mapa_consultores.keys())
        )
        status = st.selectbox("Status", options=["Todos"] + status_op)

        data = st.date_input(
            "Selecione o período",
            value=(
                df_filtrado["CRIACAO"].min(),
                df_filtrado["CRIACAO"].max(),
            ),
        )

    if not isinstance(data, tuple) or len(data) != 2:
        st.warning("Selecione um período com data inicial e final. ⚠️")
        return

    data_inicio, data_fim = data

    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)

    df_filtrado = df_filtrado[
        (df_filtrado["CRIACAO"] >= data_inicio)
        & (df_filtrado["CRIACAO"] <= data_fim)
    ]

    if filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Consultor"] == filtro]

    if status != "Todos":
        df_filtrado = df_filtrado[df_filtrado["STATUS"] == status]

    col1, col2, col3, col4, col5 = st.columns(5)

    total = len(df_filtrado)
    instaladas = (df_filtrado["STATUS"] == "INSTALADO").sum()
    agendadas = (df_filtrado["STATUS"] == "AGENDADA").sum()
    pendentes = (
        df_filtrado["STATUS"].isin(
            ["PENDENTE(AGENDAMENTO)", "PENDENTE(RETENÇÃO)"]
        )
    ).sum()
    canceladas = (df_filtrado["STATUS"] == "CANCELADO").sum()

    with col1:
        colored_header(
            label="Total",
            description="Total de fibras",
            color_name="violet-70",
        )
        st.metric(label="", value=total)

    with col2:
        colored_header(
            label="Instaladas",
            description="Fibras instaladas",
            color_name="green-70",
        )
        st.metric(label="", value=instaladas)

    with col3:
        colored_header(
            label="Agendadas",
            description="Fibras agendadas",
            color_name="yellow-80",
        )
        st.metric(label="", value=agendadas)

    with col4:
        colored_header(
            label="Pendentes",
            description="Fibras pendentes",
            color_name="orange-70",
        )
        st.metric(label="", value=pendentes)
        style_metric_cards(background_color="", border_color="#00C8FF")

    with col5:
        colored_header(
            label="Canceladas",
            description="Fibras canceladas",
            color_name="red-70",
        )
        st.metric(label="", value=canceladas)

    gb = GridOptionsBuilder.from_dataframe(df_filtrado)

    cor_status = JsCode(
        """
        function(params) {
            if (params.value === 'INSTALADO') {
                return {'backgroundColor': '#22c55e','color': '#ffffff', 'fontWeight': 'bold'};
            } else if (params.value === 'CANCELADO') {
                return {'backgroundColor': '#ef4444','color': '#ffffff', 'fontWeight': 'bold'};
            } else if (params.value === 'AGENDADA') {
                return {'backgroundColor': '#eab308','color': '#ffffff', 'fontWeight': 'bold'}; 
            } else if (params.value === 'PENDENTE(RETENÇÃO/ENRIQUECIMENTO)') {
                return {'backgroundColor': '#f97316','color': '#ffffff', 'fontWeight': 'bold'};
            } else 
                return {'backgroundColor': '#eab308','color': '#ffffff', 'fontWeight': 'bold'};
        }
        """
    )

    gb.configure_column("ID", hide=True)

    gb.configure_column("IdLoja", hide=True)

    gb.configure_column(
        "OBSERVACAO",
        editable=True,
        cellEditor="agTextEditor",
    )
    gb.configure_column(
        "STATUS",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": status_op},
        cellStyle=cor_status,
    )



    grindOptions = gb.build()

    grid_response = AgGrid(
        df_filtrado,
        gridOptions=grindOptions,
        allow_unsafe_jscode=True,
        data_return_mode="AS_INPUT",
        update_mode="VALUE_CHANGED",
        height=300,
    )

    df_editado = pd.DataFrame(grid_response["data"])

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if st.button(" 💾 Salvar alterações"):
            payload = [
                {
                    "ID": int(row["ID"]),
                    "STATUS": str(row["STATUS"]),
                    "OBSERVACAO": str(row.get("OBSERVACAO", "")),
                }
                for _, row in df_editado.iterrows()
            ]

            try:
                response = requests.post(URL_API, json=payload, timeout=10)

                if response.status_code == 200:
                    st.success("✅ Alterações salvas com sucesso!")
                    st.cache_data.clear()
                else:
                    detalhe_erro = response.json().get(
                        "detail", response.text
                    )
                    st.error(
                        f"⚠️ Falha na requisição ({response.status_code}): {detalhe_erro}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(
                    f"🚨 Não foi possível conectar ao servidor FastAPI: {e}"
                )

    with button_col2:
        if st.button("Atualizar"):
            st.cache_data.clear()
            st.rerun()

    status_criticos = [
        "PENDENTE(AGENDAMENTO)",
        "PENDENTE(RETENÇÃO/ENRIQUECIMENTO)",
        "CANCELADO",
    ]

    df_alertas = df_filtrado[
        df_filtrado["STATUS"]
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(status_criticos)
    ]

    if not df_alertas.empty:
        st.divider()
        colored_header(
            label="Painel de Tratativas de Pendências",
            description="Acompanhamento de fibras pendentes",
            color_name="violet-70",
        )

        cols = st.columns(2)
        telefones_por_loja = st.secrets.get("telefones", {})

        for idx, (_, row) in enumerate(df_alertas.iterrows()):
            status_item = str(row.get("STATUS", "N/A")).strip()
            consultor = str(row.get("Consultor", "N/A")).strip()
            ordem = str(row.get("ORDEM", "N/A")).strip()
            data_instalacao = str(row.get("INSTALACAO", "N/A")).strip()
            motivo = str(row.get("OBSERVACAO", "N/A")).strip()

            loja_id = str(row.get("IdLoja", "")).strip()
            contatos_da_loja = telefones_por_loja.get(loja_id, {})
            telefone_cru = contatos_da_loja.get(consultor, "")

            telefone_limpo = re.sub(r"\D", "", str(telefone_cru))

            if len(telefone_limpo) in [10, 11]:
                telefone_limpo = f"55{telefone_limpo}"

            mensagem_detalhada = (
                f"🚨 *TRATATIVA DE PENDÊNCIA - FIBRA*\n\n"
                f"• *Consultor:* {consultor}\n"
                f"• *Ordem:* {ordem}\n"
                f"• *Data de instalação da fibra:* {data_instalacao}\n"
                f"• *Status:* {status_item}\n"
                f"• *Motivo:* {motivo}\n\n"
                f"Favor verificar o caso junto à equipe técnica."
            )

            col_atual = cols[idx % 2]

            with col_atual:
                with st.container(border=True):
                    st.markdown(f"### 👤 {consultor}")
                    st.divider()

                    st.markdown(f"**Ordem:** {ordem}")
                    st.markdown(f"**Data:** {data_instalacao}")
                    st.markdown(f"**Status:** {status_item}")
                    st.markdown(f"**Observação/Motivo:** {motivo}")

                    if len(telefone_limpo) in [12, 13]:
                        link_wa = (
                            f"https://wa.me/{telefone_limpo}?text="
                            f"{urllib.parse.quote(mensagem_detalhada)}"
                        )

                        st.link_button(
                            "📲 Notificar no WhatsApp",
                            link_wa,
                            use_container_width=True,
                            type="secondary",
                        )
                    else:
                        st.warning(
                            f"⚠️ Telefone não cadastrado para "
                            f"'{consultor}' na loja '{loja_id}'."
                        )


def acompanhamento_diario():
    usuario = st.session_state.get("usuario_logado", {})
    cargo = usuario.get("cargo")
    loja_id_sessao = st.session_state.get("loja_id")

    loja_filtro = None if cargo == "ADM" else loja_id_sessao

    dados = buscar_backlog_api(loja_id=loja_filtro)

    if not dados:
        st.info("Nenhum registro encontrado para esta loja.")
        return

    colored_header(
        label="Backlog Diário",
        description="Fibras agendadas",
        color_name="violet-70",
    )

    df_filtrado = pd.DataFrame(dados)

    df_filtrado["CRIACAO"] = pd.to_datetime(
        df_filtrado["CRIACAO"], errors="coerce"
    )

    status_op = [
        "INSTALADO",
        "PENDENTE(AGENDAMENTO)",
        "PENDENTE(RETENÇÃO/ENRIQUECIMENTO)",
        "CANCELADO",
    ]

    with st.sidebar:
        data = st.date_input("Data")
        status_diario = st.selectbox("Status", options=["Todos"] + status_op)

    if data:
        df_filtrado = df_filtrado[df_filtrado["CRIACAO"].dt.date == data]

    if status_diario != "Todos":
        df_filtrado = df_filtrado[df_filtrado["STATUS"] == status_diario]

    agendadas = (df_filtrado["STATUS"] == "AGENDADA").sum()

    col1, col2 = st.columns(2)

    with col1:
        colored_header(
            label="Agendadas",
            description="Total de fibras para hoje",
            color_name="yellow-80",
        )
        st.metric(label="", value=agendadas)

    with col2:
        colored_header(
            label="Data",
            description="Agendadas para o dia",
            color_name="red-70",
        )
        data_objeto = datetime.now()
        data_formatada = data_objeto.strftime("%d/%m/%Y")
        st.metric(label="", value=data_formatada)

    style_metric_cards(background_color="", border_color="#00C8FF")

    gb = GridOptionsBuilder.from_dataframe(df_filtrado)

    cor_status = JsCode(
        """
        function(params) {
            if (params.value === 'INSTALADO') {
                return {'backgroundColor': '#22c55e','color': '#ffffff', 'fontWeight': 'bold'};
            } else if (params.value === 'CANCELADO') {
                return {'backgroundColor': '#ef4444','color': '#ffffff', 'fontWeight': 'bold'};
            } else if (params.value === 'AGENDADA') {
                return {'backgroundColor': '#eab308','color': '#ffffff', 'fontWeight': 'bold'}; 
            } else if (params.value === 'PENDENTE(RETENÇÃO/ENRIQUECIMENTO)') {
                return {'backgroundColor': '#f97316','color': '#ffffff', 'fontWeight': 'bold'};
            } else 
                return {'backgroundColor': '#eab308','color': '#ffffff', 'fontWeight': 'bold'};
        }
        """
    )

    gb.configure_column("ID", hide=True)

    gb.configure_column("IdLoja", hide=True)

    gb.configure_column(
        "OBSERVACAO",
        editable=True,
        cellEditor="agTextEditor",
    )
    gb.configure_column(
        "STATUS",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": status_op},
        cellStyle=cor_status,
    )

    grindOptions = gb.build()
    grindOptions["stopEditingWhenCellsLoseFocus"] = True

    if not df_filtrado.empty:
        grid_response = AgGrid(
            df_filtrado,
            gridOptions=grindOptions,
            allow_unsafe_jscode=True,
            data_return_mode="AS_INPUT",
            update_mode="VALUE_CHANGED",
            height=300,
        )

        df_editado = pd.DataFrame(grid_response["data"])

        if st.button(" 💾 Salvar alterações"):
            payload = [
                {
                    "ID": int(row["ID"]),
                    "STATUS": str(row["STATUS"]),
                    "OBSERVACAO": str(row.get("OBSERVACAO", "")),
                }
                for _, row in df_editado.iterrows()
            ]

            try:
                response = requests.post(URL_API, json=payload, timeout=10)

                if response.status_code == 200:
                    st.success("✅ Alterações salvas com sucesso!")
                    st.cache_data.clear()
                else:
                    detalhe_erro = response.json().get(
                        "detail", response.text
                    )
                    st.error(
                        f"⚠️ Falha na requisição ({response.status_code}): {detalhe_erro}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(
                    f"🚨 Não foi possível conectar ao servidor FastAPI: {e}"
                )
    else:
        st.info("Nenhum agendamento para este filtro.")


def controle_tela_gl(id_loja=None):
    with st.sidebar:
        menu_gl = option_menu(
            "Menu",
            ["Fibras do dia", "Relatorio geral"],
            menu_icon="house",
            icons=["check2-square", "file-earmark-bar-graph"],
            default_index=0,
            styles={
                "container": {
                    "background-color": "#000000ff",
                },
                "nav-link-selected": {"background-color": "#008000"},
            },
        )

    if menu_gl == "Fibras do dia":
        acompanhamento_diario()
    elif menu_gl == "Relatorio geral":
        acompanhamento_geral()