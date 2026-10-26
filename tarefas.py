"""
tarefas.py
----------
Regras de negócio do Sistema de Gerenciamento de Tarefas.

Aqui ficam as funções de cadastrar, listar/filtrar, atualizar e remover
tarefas. Elas trabalham com uma LISTA DE DICIONÁRIOS (cada dicionário é
uma tarefa) e não sabem nada sobre a tela nem sobre o arquivo:
  - a tela fica em interface.py
  - o arquivo fica em persistencia.py
Essa separação deixa o código mais fácil de testar e de dividir no grupo.

Formato de uma tarefa:
{
    "id": "a1b2c3d4",
    "descricao": "Entregar o trabalho de Python",
    "data_vencimento": "2026-10-30",     # guardada como texto no formato AAAA-MM-DD
    "status": "pendente",                # pendente | em andamento | concluída | atrasada
    "prioridade": "alta",                # baixa | média | alta          (extra)
    "categoria": "estudos",              # trabalho | pessoal | estudos | outros (extra)
    "recorrencia": "nenhuma",            # nenhuma | diária | semanal | mensal   (extra)
    "criada_em": "2026-10-26T14:30:00"
}
"""

import calendar
import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

# Valores permitidos (usados na validação e nos menus da interface)
STATUS = ["pendente", "em andamento", "concluída", "atrasada"]
PRIORIDADES = ["baixa", "média", "alta"]
CATEGORIAS = ["trabalho", "pessoal", "estudos", "outros"]
RECORRENCIAS = ["nenhuma", "diária", "semanal", "mensal"]

# Campos que o usuário pode alterar ao editar uma tarefa
CAMPOS_EDITAVEIS = {"descricao", "data_vencimento", "status", "prioridade", "categoria", "recorrencia"}

# Usado para ordenar: quanto menor o número, mais importante
PESO_PRIORIDADE = {"alta": 0, "média": 1, "baixa": 2}

# O servidor do Streamlit Cloud fica em outro fuso horário (UTC).
# Usamos o horário de Brasília para que "hoje" seja o hoje do usuário.
FUSO = ZoneInfo("America/Sao_Paulo")


# ------------------------------------------------------------------ utilidades

def hoje():
    """Data de hoje no horário de Brasília."""
    return datetime.now(FUSO).date()


def para_data(valor):
    """Converte 'AAAA-MM-DD' (texto) ou um objeto date em um objeto date."""
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))


def esta_atrasada(tarefa):
    """
    Diz se a data de vencimento já passou e a tarefa não foi concluída.
    Serve para mostrar o aviso "Vencida". Não muda o status sozinho:
    quem decide a coluna/status é o usuário.
    """
    return tarefa["status"] != "concluída" and para_data(tarefa["data_vencimento"]) < hoje()


def proxima_data(data_atual, recorrencia):
    """Calcula a próxima data de vencimento de uma tarefa recorrente."""
    if recorrencia == "diária":
        return data_atual + timedelta(days=1)
    if recorrencia == "semanal":
        return data_atual + timedelta(weeks=1)
    if recorrencia == "mensal":
        ano = data_atual.year + data_atual.month // 12   # dezembro -> vira o ano
        mes = data_atual.month % 12 + 1
        # Se o dia não existir no mês seguinte (ex.: 31/01 -> fevereiro), usa o último dia do mês
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        return date(ano, mes, min(data_atual.day, ultimo_dia))
    return None


def _novo_id():
    """Gera um identificador curto e único para a tarefa."""
    return uuid.uuid4().hex[:8]


def _validar(dados):
    """Confere os valores informados. Lança ValueError com uma mensagem clara se algo estiver errado."""
    if "descricao" in dados and not str(dados["descricao"]).strip():
        raise ValueError("A descrição não pode ficar vazia.")

    if "data_vencimento" in dados:
        try:
            para_data(dados["data_vencimento"])
        except ValueError:
            raise ValueError("Data de vencimento inválida. Use o formato AAAA-MM-DD.")

    opcoes = {
        "status": STATUS,
        "prioridade": PRIORIDADES,
        "categoria": CATEGORIAS,
        "recorrencia": RECORRENCIAS,
    }
    for campo, permitidos in opcoes.items():
        if campo in dados and dados[campo] not in permitidos:
            raise ValueError(f"Valor inválido para {campo}: '{dados[campo]}'. Use: {', '.join(permitidos)}.")


def normalizar_tarefa(dado):
    """
    Garante que uma tarefa tenha todos os campos no formato certo.
    É usada ao cadastrar e também ao ler do arquivo (preenche campos que faltarem).
    Lança ValueError se faltar algo obrigatório ou se algum valor for inválido.
    """
    if not isinstance(dado, dict):
        raise ValueError("Cada tarefa precisa ser um dicionário.")

    for obrigatorio in ("descricao", "data_vencimento", "status"):
        if obrigatorio not in dado:
            raise ValueError(f"Tarefa sem o campo obrigatório '{obrigatorio}'.")

    _validar(dado)

    return {
        "id": str(dado.get("id") or _novo_id()),
        "descricao": str(dado["descricao"]).strip(),
        "data_vencimento": para_data(dado["data_vencimento"]).isoformat(),
        "status": dado["status"],
        "prioridade": dado.get("prioridade", "média"),
        "categoria": dado.get("categoria", "outros"),
        "recorrencia": dado.get("recorrencia", "nenhuma"),
        "criada_em": dado.get("criada_em") or datetime.now(FUSO).isoformat(timespec="seconds"),
    }


# -------------------------------------------------------------- CRUD (cadastro)

def criar_tarefa(tarefas, descricao, data_vencimento, status="pendente",
                 prioridade="média", categoria="outros", recorrencia="nenhuma"):
    """Cadastra uma nova tarefa na lista e devolve a tarefa criada."""
    tarefa = normalizar_tarefa({
        "descricao": descricao,
        "data_vencimento": data_vencimento,
        "status": status,
        "prioridade": prioridade,
        "categoria": categoria,
        "recorrencia": recorrencia,
    })
    tarefas.append(tarefa)
    return tarefa


def buscar_tarefa(tarefas, id_tarefa):
    """Procura uma tarefa pelo id. Devolve None se não encontrar."""
    for tarefa in tarefas:
        if tarefa["id"] == id_tarefa:
            return tarefa
    return None


def filtrar_tarefas(tarefas, status=None, data_inicio=None, data_fim=None,
                    categorias=None, prioridades=None, texto=""):
    """
    Devolve só as tarefas que passam em TODOS os filtros informados.
    Filtro com valor None = não filtrar por aquele campo.
      status, categorias, prioridades -> listas de valores aceitos
      data_inicio, data_fim           -> intervalo de vencimento (inclusive)
      texto                           -> trecho procurado na descrição
    """
    texto = texto.strip().lower()
    resultado = []
    for t in tarefas:
        vencimento = para_data(t["data_vencimento"])
        if status is not None and t["status"] not in status:
            continue
        if data_inicio is not None and vencimento < data_inicio:
            continue
        if data_fim is not None and vencimento > data_fim:
            continue
        if categorias is not None and t["categoria"] not in categorias:
            continue
        if prioridades is not None and t["prioridade"] not in prioridades:
            continue
        if texto and texto not in t["descricao"].lower():
            continue
        resultado.append(t)
    return resultado


def ordenar_tarefas(tarefas, criterio="vencimento"):
    """Ordena por data de vencimento ou por prioridade. Concluídas sempre vão para o fim."""
    if criterio == "prioridade":
        def chave(t):
            return (t["status"] == "concluída", PESO_PRIORIDADE[t["prioridade"]], t["data_vencimento"])
    else:
        def chave(t):
            return (t["status"] == "concluída", t["data_vencimento"], PESO_PRIORIDADE[t["prioridade"]])
    return sorted(tarefas, key=chave)


def atualizar_tarefa(tarefas, id_tarefa, **alteracoes):
    """
    Altera um ou mais campos de uma tarefa.
    Exemplos:
        atualizar_tarefa(lista, "a1b2c3d4", status="concluída")
        atualizar_tarefa(lista, "a1b2c3d4", descricao="Nova descrição", data_vencimento=date(2026, 11, 5))

    Extra (recorrência): ao concluir uma tarefa recorrente, a próxima é criada
    automaticamente. Nesse caso a função devolve a nova tarefa; senão devolve None.
    """
    tarefa = buscar_tarefa(tarefas, id_tarefa)
    if tarefa is None:
        raise ValueError("Tarefa não encontrada.")

    campos_invalidos = set(alteracoes) - CAMPOS_EDITAVEIS
    if campos_invalidos:
        raise ValueError(f"Não é possível alterar: {', '.join(campos_invalidos)}.")

    _validar(alteracoes)
    if "descricao" in alteracoes:
        alteracoes["descricao"] = str(alteracoes["descricao"]).strip()
    if "data_vencimento" in alteracoes:
        alteracoes["data_vencimento"] = para_data(alteracoes["data_vencimento"]).isoformat()

    estava_concluida = tarefa["status"] == "concluída"
    tarefa.update(alteracoes)

    nova = None
    acabou_de_concluir = not estava_concluida and tarefa["status"] == "concluída"
    if acabou_de_concluir and tarefa["recorrencia"] != "nenhuma":
        proxima = proxima_data(para_data(tarefa["data_vencimento"]), tarefa["recorrencia"])
        nova = criar_tarefa(tarefas, tarefa["descricao"], proxima, "pendente",
                            tarefa["prioridade"], tarefa["categoria"], tarefa["recorrencia"])
        # A recorrência "passa" para a nova tarefa. Assim, se a antiga for reaberta
        # e concluída de novo, não cria uma cópia duplicada.
        tarefa["recorrencia"] = "nenhuma"
    return nova


def remover_tarefa(tarefas, id_tarefa):
    """Exclui a tarefa. Devolve True se removeu e False se não encontrou."""
    tarefa = buscar_tarefa(tarefas, id_tarefa)
    if tarefa is None:
        return False
    tarefas.remove(tarefa)
    return True


def resumo(tarefas):
    """Conta as tarefas por status, o total e quantas já passaram da data."""
    contagem = {s: 0 for s in STATUS}
    for t in tarefas:
        contagem[t["status"]] += 1
    contagem["total"] = len(tarefas)
    contagem["vencidas"] = sum(1 for t in tarefas if esta_atrasada(t))
    return contagem
