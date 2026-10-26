# ✅ Gerenciador de Tarefas

Projeto da disciplina **Computational Thinking with Python** (FIAP).
Aplicação web feita 100% em Python com [Streamlit](https://streamlit.io) para cadastrar,
listar, filtrar, editar e excluir tarefas. As tarefas ficam salvas em um arquivo JSON.

## Funcionalidades

- **Quadro estilo Trello**: arraste os cartões livremente entre Pendentes, Em andamento,
  Concluídas e Atrasadas; tarefas que passaram da data ganham a marca "vencida"
- **Cadastrar** tarefa com descrição, data de vencimento e status (pendente, em andamento, concluída e, como extra, atrasada)
- **Listar** todas as tarefas, com **filtro por status** e **por data de vencimento**
  (atrasadas, hoje, próximos 7 dias, data específica ou intervalo)
- **Atualizar**: editar descrição, data e status (botões rápidos Iniciar / Concluir / Reabrir)
- **Remover** tarefa (com confirmação)
- **Salvar e carregar** automaticamente em `dados/tarefas.json`
- Extras: prioridade, categoria, tarefas recorrentes (diária, semanal, mensal),
  busca por texto, painel de resumo e backup/restauração em JSON

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Ponto de entrada (é ele que o Streamlit executa) |
| `interface.py` | Telas, menus e formulários (Streamlit) |
| `estilo.py` | Visual inspirado na FIAP (CSS e HTML da interface) |
| `.streamlit/config.toml` | Tema do app (cores preto e rosa) |
| `quadro.py` | Lógica do quadro (em qual coluna cada tarefa fica e o que acontece ao arrastar) |
| `tarefas.py` | Regras: cadastrar, filtrar, ordenar, atualizar e remover |
| `persistencia.py` | Salvar e carregar as tarefas no arquivo JSON |
| `requirements.txt` | Bibliotecas necessárias |

## Como rodar no computador

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

O navegador abre em `http://localhost:8501`.

## Como publicar no Streamlit Community Cloud

1. Suba esta pasta para um repositório **público** no GitHub.
2. Acesse <https://share.streamlit.io> e entre com sua conta do GitHub.
3. Clique em **Create app** → escolha o repositório, a branch (`main`) e em
   *Main file path* coloque `app.py`.
4. Clique em **Deploy** e aguarde alguns minutos.

> ⚠️ No Streamlit Cloud o arquivo `dados/tarefas.json` é apagado quando o app reinicia
> (nova versão do código ou muito tempo sem uso), e todos que acessam o link
> compartilham as mesmas tarefas. Use a aba **💾 Backup** para baixar e restaurar.

## Integrantes

- Nome — RM
- Nome — RM
