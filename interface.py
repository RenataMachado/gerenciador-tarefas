"""
interface.py
------------
Interface web feita com Streamlit: menus, formulários e exibição das tarefas.
Este arquivo só cuida da TELA. Quem faz o trabalho de verdade são:
  - tarefas.py       -> regras (cadastrar, filtrar, atualizar, remover)
  - persistencia.py  -> arquivo (salvar e carregar)

Como o Streamlit funciona: a cada clique, o script inteiro roda de novo
de cima para baixo. Por isso, a cada execução lemos as tarefas do arquivo,
e depois de qualquer alteração salvamos e mandamos a tela recarregar (st.rerun).
"""

import hashlib
import json
from datetime import timedelta

import streamlit as st
from streamlit_sortables import sort_items

import estilo as es
import persistencia as ps
import quadro as qd
import tarefas as tf

FILTROS_DATA = [
    "Todas as datas",
    "Vencidas (data já passou)",
    "Vencem hoje",
    "Próximos 7 dias",
    "Data específica",
    "Intervalo de datas",
]


# ------------------------------------------------------------------ utilidades

def br(data_iso):
    """Converte '2026-10-26' em '26/10/2026' para mostrar na tela."""
    return tf.para_data(data_iso).strftime("%d/%m/%Y")


def chave(tarefa, nome):
    """
    Cria uma key única para cada campo/botão de uma tarefa.
    A key inclui uma "assinatura" do conteúdo da tarefa: se ela mudar
    (ex.: alguém clicou em Concluir), o formulário de edição é recriado
    já com os valores novos, em vez de continuar mostrando os antigos.
    """
    assinatura = hashlib.md5(json.dumps(tarefa, sort_keys=True).encode()).hexdigest()[:6]
    return f"{nome}_{tarefa['id']}_{assinatura}"


def salvar_e_avisar(lista, mensagem):
    """Grava no arquivo, guarda a mensagem de aviso e recarrega a tela."""
    ps.salvar_tarefas(lista)
    st.session_state["aviso"] = mensagem
    st.rerun()


def mudar_status(lista, id_tarefa, novo_status):
    """Ação rápida dos botões Iniciar / Concluir / Reabrir."""
    nova = tf.atualizar_tarefa(lista, id_tarefa, status=novo_status)
    mensagens = {
        "em andamento": "Tarefa iniciada.",
        "concluída": "Tarefa concluída!",
        "pendente": "Tarefa reaberta.",
        "atrasada": "Tarefa marcada como atrasada.",
    }
    mensagem = mensagens[novo_status]
    if nova:
        mensagem += f" A próxima foi criada para {br(nova['data_vencimento'])}."
    salvar_e_avisar(lista, mensagem)


# ------------------------------------------------------------------ partes da tela

def tela_cadastrar(lista):
    """Aba Nova tarefa."""
    st.subheader("Cadastrar tarefa")

    with st.form("form_nova_tarefa", clear_on_submit=True):
        descricao = st.text_input("Descrição *", placeholder="Ex.: Entregar o trabalho de Python",
                                  key="nova_descricao")
        c1, c2 = st.columns(2)
        vencimento = c1.date_input("Data de vencimento *", value=tf.hoje(), format="DD/MM/YYYY",
                                   key="nova_data")
        status = c2.selectbox("Status", tf.STATUS, key="novo_status")

        c3, c4, c5 = st.columns(3)
        prioridade = c3.selectbox("Prioridade", tf.PRIORIDADES, index=1, key="nova_prioridade")
        categoria = c4.selectbox("Categoria", tf.CATEGORIAS, key="nova_categoria")
        recorrencia = c5.selectbox("Repetir", tf.RECORRENCIAS, key="nova_recorrencia",
                                   help="Ao concluir uma tarefa que se repete, a próxima é criada sozinha.")

        enviado = st.form_submit_button("Cadastrar tarefa", type="primary")

    if enviado:
        try:
            tf.criar_tarefa(lista, descricao, vencimento, status, prioridade, categoria, recorrencia)
        except ValueError as erro:
            st.error(erro)
        else:
            salvar_e_avisar(lista, "Tarefa cadastrada!")


def tela_listar(lista):
    """Aba Lista: filtros + lista de cartões."""
    st.subheader("Lista de tarefas")

    if not lista:
        st.info("Nenhuma tarefa cadastrada ainda. Abra a aba **Nova tarefa** para criar a primeira.")
        return

    # ---------------- filtros
    with st.container(border=True):
        st.markdown("**Filtros**")
        c1, c2 = st.columns(2)
        # "or None" -> se nada for escolhido, não filtra (mostra todos)
        status = c1.multiselect("Status", tf.STATUS, placeholder="Todos", key="filtro_status") or None
        tipo_data = c2.selectbox("Data de vencimento", FILTROS_DATA, key="filtro_tipo_data")

        hoje = tf.hoje()
        data_inicio = data_fim = None
        if tipo_data == "Vencidas (data já passou)":
            data_fim = hoje - timedelta(days=1)
            status = [s for s in (status or tf.STATUS) if s != "concluída"]
        elif tipo_data == "Vencem hoje":
            data_inicio = data_fim = hoje
        elif tipo_data == "Próximos 7 dias":
            data_inicio, data_fim = hoje, hoje + timedelta(days=7)
        elif tipo_data == "Data específica":
            data_inicio = data_fim = c2.date_input("Escolha a data", hoje, format="DD/MM/YYYY",
                                                   key="filtro_data")
        elif tipo_data == "Intervalo de datas":
            intervalo = c2.date_input("Escolha o intervalo", (hoje, hoje + timedelta(days=30)),
                                      format="DD/MM/YYYY", key="filtro_intervalo")
            # Enquanto o usuário escolhe, o calendário pode devolver só a primeira data
            if len(intervalo) == 2:
                data_inicio, data_fim = intervalo
            elif len(intervalo) == 1:
                data_inicio = data_fim = intervalo[0]

        c3, c4, c5, c6 = st.columns(4)
        categorias = c3.multiselect("Categoria", tf.CATEGORIAS, placeholder="Todas",
                                    key="filtro_categoria") or None
        prioridades = c4.multiselect("Prioridade", tf.PRIORIDADES, placeholder="Todas",
                                     key="filtro_prioridade") or None
        texto = c5.text_input("Buscar na descrição", key="filtro_texto")
        ordem = c6.selectbox("Ordenar por", ["vencimento", "prioridade"],
                             format_func=str.capitalize, key="filtro_ordem")

    # ---------------- resultado
    filtradas = tf.filtrar_tarefas(lista, status, data_inicio, data_fim, categorias, prioridades, texto)
    filtradas = tf.ordenar_tarefas(filtradas, ordem)

    st.caption(f"Mostrando {len(filtradas)} de {len(lista)} tarefa(s).")
    if not filtradas:
        st.warning("Nenhuma tarefa encontrada com esses filtros. Tente limpar algum deles.")

    for tarefa in filtradas:
        cartao_tarefa(lista, tarefa)


def cartao_tarefa(lista, tarefa):
    """Mostra uma tarefa com ações rápidas, edição e exclusão."""
    # A key do container leva o status (ex.: card-andamento-a1b2c3d4).
    # O CSS em estilo.py usa isso para pintar a borda do cartão de acordo com o status.
    slug = es.SLUG_STATUS[tarefa["status"]]
    with st.container(key=f"card-{slug}-{tarefa['id']}"):
        info, acoes = st.columns([5, 1], vertical_alignment="center")

        info.markdown(
            es.cartao_html(tarefa, br(tarefa["data_vencimento"]), tf.esta_atrasada(tarefa)),
            unsafe_allow_html=True,
        )

        # Botões de ação rápida
        if tarefa["status"] == "pendente":
            if acoes.button("Iniciar", key=chave(tarefa, "iniciar")):
                mudar_status(lista, tarefa["id"], "em andamento")
        if tarefa["status"] != "concluída":
            if acoes.button("Concluir", key=chave(tarefa, "concluir"), type="primary"):
                mudar_status(lista, tarefa["id"], "concluída")
        else:
            if acoes.button("Reabrir", key=chave(tarefa, "reabrir")):
                mudar_status(lista, tarefa["id"], "pendente")

        with st.expander("Editar ou excluir"):
            formulario_edicao(lista, tarefa, "lista")


def formulario_edicao(lista, tarefa, origem):
    """
    Formulário para editar todos os campos de uma tarefa, e a opção de excluir.
    'origem' diferencia as keys, porque o mesmo formulário aparece no Quadro e na Lista.
    """
    def k(nome):
        return chave(tarefa, f"{origem}-{nome}")

    with st.form(k("form_editar")):
        descricao = st.text_input("Descrição", tarefa["descricao"], key=k("descricao"))
        c1, c2 = st.columns(2)
        vencimento = c1.date_input("Data de vencimento", tf.para_data(tarefa["data_vencimento"]),
                                   format="DD/MM/YYYY", key=k("data"))
        status = c2.selectbox("Status", tf.STATUS, index=tf.STATUS.index(tarefa["status"]),
                              key=k("status"))

        c3, c4, c5 = st.columns(3)
        prioridade = c3.selectbox("Prioridade", tf.PRIORIDADES,
                                  index=tf.PRIORIDADES.index(tarefa["prioridade"]),
                                  key=k("prioridade"))
        categoria = c4.selectbox("Categoria", tf.CATEGORIAS,
                                 index=tf.CATEGORIAS.index(tarefa["categoria"]),
                                 key=k("categoria"))
        recorrencia = c5.selectbox("Repetir", tf.RECORRENCIAS,
                                   index=tf.RECORRENCIAS.index(tarefa["recorrencia"]),
                                   key=k("recorrencia"))

        salvar = st.form_submit_button("Salvar alterações", type="primary")

    if salvar:
        try:
            nova = tf.atualizar_tarefa(
                lista, tarefa["id"],
                descricao=descricao, data_vencimento=vencimento, status=status,
                prioridade=prioridade, categoria=categoria, recorrencia=recorrencia,
            )
        except ValueError as erro:
            st.error(erro)
        else:
            mensagem = "Alterações salvas."
            if nova:
                mensagem += f" A próxima foi criada para {br(nova['data_vencimento'])}."
            salvar_e_avisar(lista, mensagem)

    # Exclusão com confirmação, para evitar apagar sem querer
    st.divider()
    confirmar = st.checkbox("Quero excluir esta tarefa", key=k("confirmar"))
    if st.button("Excluir tarefa", key=k("excluir"), disabled=not confirmar):
        tf.remover_tarefa(lista, tarefa["id"])
        salvar_e_avisar(lista, "Tarefa excluída.")


def tela_quadro(lista):
    """Aba Quadro: kanban estilo Trello, com cartões que podem ser arrastados."""
    st.subheader("Quadro de tarefas")
    if not lista:
        st.info("Nenhuma tarefa cadastrada ainda. Abra a aba **Nova tarefa** para criar a primeira.")
        return
    st.caption("Arraste os cartões livremente entre as colunas para mudar o status. "
               "Cartões marcados com “vencida” já passaram da data.")

    estrutura, ids = qd.montar_quadro(lista)

    # A key muda sempre que as tarefas mudam, para o quadro ser redesenhado com os dados novos
    versao = st.session_state.get("versao_quadro", 0)
    assinatura = hashlib.md5(json.dumps(estrutura).encode()).hexdigest()[:8]
    resultado = sort_items(
        estrutura,
        multi_containers=True,
        direction="vertical",          # colunas lado a lado, cartões empilhados
        custom_style=es.CSS_QUADRO,
        key=f"quadro_{versao}_{assinatura}",
    )

    if resultado and resultado != estrutura:
        mensagens = qd.aplicar_movimentos(lista, estrutura, resultado, ids)
        st.session_state["versao_quadro"] = versao + 1
        if mensagens:
            salvar_e_avisar(lista, " ".join(mensagens))
        else:
            st.rerun()   # só mudou a ordem dentro da coluna: volta para a ordem por data

    # Editar ou excluir a partir do quadro
    st.markdown("**Editar ou excluir uma tarefa**")
    por_id = {t["id"]: t for t in tf.ordenar_tarefas(lista)}
    escolhida = st.selectbox(
        "Tarefa", list(por_id), index=None, placeholder="Escolha uma tarefa",
        format_func=lambda id_tarefa: qd.rotulo(por_id[id_tarefa]),
        key="quadro_tarefa_escolhida", label_visibility="collapsed",
    )
    if escolhida in por_id:
        with st.container(border=True):
            formulario_edicao(lista, por_id[escolhida], "quadro")


def tela_backup(lista):
    """Aba Backup: baixar e restaurar as tarefas."""
    st.subheader("Backup")
    st.write(
        "As tarefas são salvas automaticamente no arquivo `dados/tarefas.json` a cada alteração. "
        "Aqui você pode baixar uma cópia ou restaurar um backup."
    )
    st.info(
        "No Streamlit Community Cloud o arquivo é apagado quando o app reinicia "
        "(atualização do código ou longo tempo sem uso). Baixe um backup de vez em quando.",
        icon="ℹ️",
    )

    st.download_button(
        "Baixar backup (JSON)",
        data=ps.exportar_json(lista),
        file_name=f"tarefas_{tf.hoje().isoformat()}.json",
        mime="application/json",
        disabled=not lista,
    )

    st.divider()
    arquivo = st.file_uploader("Restaurar backup", type=["json"], key="arquivo_backup")
    modo = st.radio("Como restaurar?", ["Juntar com as tarefas atuais", "Substituir todas as tarefas"],
                    key="modo_backup")

    if arquivo and st.button("Restaurar backup", type="primary"):
        try:
            importadas = ps.importar_json(arquivo.getvalue())
        except ValueError as erro:
            st.error(f"Não foi possível restaurar: {erro}")
            return

        if modo.startswith("Substituir"):
            salvar_e_avisar(importadas, f"Backup restaurado: {len(importadas)} tarefa(s).")
        else:
            ids_atuais = {t["id"] for t in lista}
            novas = [t for t in importadas if t["id"] not in ids_atuais]
            salvar_e_avisar(lista + novas, f"Backup restaurado: {len(novas)} tarefa(s) adicionada(s).")


# ------------------------------------------------------------------ página principal

def main():
    st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="✅", layout="wide")

    # Mostra o aviso da última ação (guardado antes do st.rerun)
    aviso = st.session_state.pop("aviso", None)
    if aviso:
        st.toast(aviso)

    # O arquivo é a "fonte da verdade": lemos dele a cada execução
    lista = ps.carregar_tarefas()

    es.aplicar_estilo()
    st.markdown(es.cabecalho(), unsafe_allow_html=True)
    st.markdown(es.painel_resumo(tf.resumo(lista)), unsafe_allow_html=True)

    aba_quadro, aba_lista, aba_nova, aba_backup = st.tabs(["Quadro", "Lista", "Nova tarefa", "Backup"])
    with aba_quadro:
        tela_quadro(lista)
    with aba_lista:
        tela_listar(lista)
    with aba_nova:
        tela_cadastrar(lista)
    with aba_backup:
        tela_backup(lista)
