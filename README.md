# Estagiaê

Este é um bot básico desenvolvido para a disciplina de Gestão Estratégica de TI 
24.2 com o intuito de facilitar a solicitação de estágios pelos alunos do DCC.

## Funcionalidades [WIP]
- Responde ao comando `/start` com uma mensagem de boas-vindas.
- Ecoa qualquer mensagem de texto enviada pelo usuário.

## Configuração do Ambiente
### Pré-requisitos
- Python 3.9 ou superior
- Biblioteca `python-telegram-bot`
- Biblioteca `python-dotenv`

### Instalação
1. Clone este repositório:
   ```bash
   git clone https://github.com/TeaH4nd/estagiae_bot.git
   cd estagiae_bot
   ```
2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv 
   source venv/bin/activate
   # C:\> venv\Scripts\activate.bat - cmd
   # PS C:\> <venv>\Scripts\Activate.ps1 - PowerShell
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração do Token
1. Crie um arquivo .env na raiz do projeto.

2. Adicione o token do bot fornecido pelo BotFather:
    ```
    TELEGRAM_TOKEN=seu_token_aqui
    ```

## Como executar o Bot
1. Certifique-se de que o arquivo .env contém o token correto.
2. Ative o ambiente virtual
    ```bash
   source venv/bin/activate
   # C:\> venv\Scripts\activate.bat - cmd
   # PS C:\> <venv>\Scripts\Activate.ps1 - PowerShell
   ```
2. Execute o script do bot:
    ```bash
    python estagiae_bot.py
    ```
3. No Telegram, inicie uma conversa com o bot e envie mensagens para interagir.
