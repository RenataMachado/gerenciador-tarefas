"""
quadro.py
---------
Lógica do quadro estilo Trello (kanban): em qual coluna cada tarefa aparece
e o que acontece quando um cartão é arrastado para outra coluna.
Aqui não tem nada de tela; o desenho do quadro fica em interface.py.

Cada coluna corresponde a um status. O cartão pode ser arrastado
livremente para qualquer coluna, e o status da tarefa muda junto.
Tarefas que passaram da data e não estão em Atrasadas ganham a marca "vencida".
"""

import tarefas as tf

COLUNAS = ["Pendentes", "Em andamento", "Concluídas", "Atrasadas"]
STATUS_DA_COLUNA = {
    "Pendentes": "pendente",
    "Em andamento": "em andamento",
    "Concluídas": "concluída",
    "Atrasadas": "atrasada",
}
COLUNA_DO_STATUS = {status: coluna for coluna, status in STATUS_DA_COLUNA.items()}


def coluna_da_tarefa(tarefa):
    """Diz em qual coluna do quadro a tarefa deve aparecer (depende só do status)."""
    return COLUNA_DO_STATUS[tarefa["status"]]


def rotulo(tarefa):
    """Texto do cartão. Ex.: 'Estudar Python · 30/10 · alta'"""
    data = tf.para_data(tarefa["data_vencimento"]).strftime("%d/%m")
    texto = f"{tarefa['descricao']} · {data}"
    if tarefa["prioridade"] == "alta":
        texto += " · alta"
    if tf.esta_atrasada(tarefa) and tarefa["status"] != "atrasada":
        texto += " · vencida"
    return texto


def montar_quadro(tarefas):
    """
    Monta o quadro no formato que o componente streamlit-sortables espera.
    Devolve:
      quadro -> [{"header": "Pendentes (2)", "items": ["Estudar · 30/10", ...]}, ...]
      ids    -> dicionário {texto do cartão: id da tarefa}, para saber quem foi arrastado
    """
    itens = {coluna: [] for coluna in COLUNAS}
    ids = {}
    for tarefa in tf.ordenar_tarefas(tarefas):
        texto = rotulo(tarefa)
        # O componente identifica os cartões pelo texto, então ele precisa ser único
        base, numero = texto, 2
        while texto in ids:
            texto = f"{base} ({numero})"
            numero += 1
        ids[texto] = tarefa["id"]
        itens[coluna_da_tarefa(tarefa)].append(texto)

    quadro = [{"header": f"{coluna} ({len(itens[coluna])})", "items": itens[coluna]} for coluna in COLUNAS]
    return quadro, ids


def aplicar_movimentos(tarefas, antes, depois, ids):
    """
    Compara o quadro antes e depois do arraste e muda o status das tarefas
    que trocaram de coluna. Devolve uma lista de mensagens para o usuário.
    """
    coluna_antes = {}
    for posicao, coluna in enumerate(antes):
        for texto in coluna["items"]:
            coluna_antes[texto] = COLUNAS[posicao]

    mensagens = []
    for posicao, coluna in enumerate(depois):
        destino = COLUNAS[posicao]
        for texto in coluna["items"]:
            origem = coluna_antes.get(texto)
            if origem is None or origem == destino:
                continue   # não mudou de coluna (no máximo mudou de posição)

            tarefa = tf.buscar_tarefa(tarefas, ids[texto])
            nova = tf.atualizar_tarefa(tarefas, tarefa["id"], status=STATUS_DA_COLUNA[destino])
            mensagem = f"“{tarefa['descricao']}” movida para {destino}."
            if nova:
                proxima = tf.para_data(nova["data_vencimento"]).strftime("%d/%m/%Y")
                mensagem += f" A próxima foi criada para {proxima}."
            mensagens.append(mensagem)
    return mensagens
