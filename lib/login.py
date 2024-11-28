import json
import os


# Diretório principal para armazenar dados dos usuários
BASE_DIR = "user_data"


# Função para obter o caminho da pasta do usuário
def get_user_dir(user_id):
    return os.path.join(BASE_DIR, str(user_id))

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
