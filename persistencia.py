"""
persistencia.py
---------------
Funções para salvar e carregar as tarefas em um arquivo JSON,
para que nada se perca ao fechar o programa.

O arquivo fica em:  dados/tarefas.json  (a pasta é criada automaticamente)
"""

import json
from datetime import datetime
from pathlib import Path

from tarefas import normalizar_tarefa

PASTA_DADOS = Path(__file__).resolve().parent / "dados"
ARQUIVO_TAREFAS = PASTA_DADOS / "tarefas.json"


def carregar_tarefas(caminho=ARQUIVO_TAREFAS):
    """
    Lê as tarefas do arquivo e devolve uma lista.
    - Se o arquivo ainda não existe (primeira vez), devolve lista vazia.
    - Se o arquivo estiver corrompido, guarda uma cópia dele com outro nome
      (para não perder nada) e começa com a lista vazia.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return []

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return [normalizar_tarefa(item) for item in dados]
    except (ValueError, TypeError):   # JSON inválido ou tarefa com dados errados
        carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
        caminho.rename(caminho.with_name(f"tarefas_corrompido_{carimbo}.json"))
        return []


def salvar_tarefas(tarefas, caminho=ARQUIVO_TAREFAS):
    """
    Grava a lista de tarefas no arquivo JSON.
    Primeiro escreve num arquivo temporário e só depois troca pelo original:
    assim, se algo der errado no meio da gravação, o arquivo antigo continua inteiro.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(".tmp")
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(tarefas, arquivo, ensure_ascii=False, indent=2)
    temporario.replace(caminho)


def exportar_json(tarefas):
    """Transforma as tarefas em bytes de JSON (usado no botão de baixar backup)."""
    return json.dumps(tarefas, ensure_ascii=False, indent=2).encode("utf-8")


def importar_json(conteudo):
    """
    Lê um backup enviado pelo usuário (bytes) e devolve a lista de tarefas.
    Lança ValueError com uma mensagem clara se o arquivo não for válido.
    """
    try:
        dados = json.loads(conteudo.decode("utf-8"))
    except ValueError:
        raise ValueError("o arquivo enviado não é um JSON válido.")

    if not isinstance(dados, list):
        raise ValueError("o JSON precisa conter uma lista de tarefas.")

    return [normalizar_tarefa(item) for item in dados]
