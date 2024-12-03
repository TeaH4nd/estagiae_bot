import json
import os

from telegram import Update
from telegram.ext import CallbackContext

from lib.consts.comissaoId import COMISSAO


# Diretório principal para armazenar dados dos usuários
BASE_DIR = "user_data"
ALUNO_DIR = os.path.join(BASE_DIR, "alunos")
COMISSAO_DIR = os.path.join(BASE_DIR, "comissao")


# Função para obter o caminho da pasta do usuário
def get_user_dir(user_id):
    if check_user_role(user_id) == "comissao":
        return os.path.join(COMISSAO_DIR, str(user_id))
    return os.path.join(ALUNO_DIR, str(user_id))

# Função para obter o caminho do arquivo de dados do usuário
def get_user_data_file(user_id):
    return os.path.join(get_user_dir(user_id), "dados.json")

# Função para salvar os dados do usuário
def save_user_data(user_id, dados):
    user_dir = get_user_dir(user_id)
    os.makedirs(user_dir, exist_ok=True)
    with open(get_user_data_file(user_id), "w") as file:
        json.dump(dados, file)

# Função para carregar os dados do usuário
def load_user_data(user_id):
    try:
        with open(get_user_data_file(user_id), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def load_user_data_from_dre(dre):
    for user_id in os.listdir(ALUNO_DIR):
        dados = load_user_data(user_id)
        if dados.get("dre") == dre:
            return dados
    return {}

async def get_user_data(update: Update, context: CallbackContext) -> None:
    """Exibe os dados salvos na sessão do usuário."""
    user_id = str(update.effective_user.id)
    dados = load_user_data(user_id)

    if dados:
        resposta = (
            f"**Seus Dados Salvos:**\n"
            f"**Nome Civil:** {dados['nome_civil']}\n"
            f"**DRE:** {dados['dre']}\n"
            f"**CR Acumulado:** {dados['cr_acumulado']}\n"
            f"**Códigos de Disciplinas:** {
                ', '.join(dados['codigos_disciplinas'])}\n"
        )
    else:
        resposta = "Nenhum dado salvo para este usuário. Envie um boletim em PDF para começar."
    await update.message.reply_text(resposta, parse_mode="Markdown")

async def get_user_status(update: Update, context: CallbackContext) -> None:
    """Exibe o status do pedido de estágio do usuário."""
    user_id = str(update.effective_user.id)
    dados = load_user_data(user_id)
    status = dados.get("status", "Desconhecido")
    await update.message.reply_text(f"Seu status atual é: {status}")

def check_user_role(user_id):
    if str(user_id) in COMISSAO:
        return "comissao"
    return "aluno"

def get_alunos():
    """Retorna a lista de alunos."""
    alunos = []

    # Verifica se o diretório base existe
    if not os.path.exists(ALUNO_DIR):
        print("O diretório de dados dos alunos não existe.")
        return alunos

    # Percorre cada pasta no diretório base
    for user_id in os.listdir(ALUNO_DIR):
        user_dir = os.path.join(ALUNO_DIR, user_id)
        dados_file = os.path.join(user_dir, "dados.json")

        # Verifica se o arquivo de dados existe
        if os.path.isfile(dados_file):
            try:
                # Carrega os dados do aluno
                with open(dados_file, "r") as file:
                    dados = json.load(file)
                aluno = {
                    "nome_civil": dados.get("nome_civil", "Não informado"),
                    "dre": dados.get("dre", "Não informado"),
                    "status": dados.get("status", "Não informado"),
                }
                alunos.append(aluno)
            except Exception as e:
                print(f"Erro ao carregar os dados do aluno {user_id}: {e}")
        else:
            print(f"Arquivo 'dados.json' não encontrado para o aluno {user_id}.")
    
    return alunos