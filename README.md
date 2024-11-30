# **Estagiaê**

O **Estagiaê** é um bot desenvolvido para a disciplina de Gestão Estratégica de TI (24.2), com o objetivo de facilitar a solicitação de estágios pelos alunos do Departamento de Ciência da Computação (DCC). Ele ajuda a validar os requisitos necessários e enviar solicitações de estágio diretamente para a comissão responsável.

---

## **Funcionalidades**
- Responde ao comando `/start` com uma mensagem personalizada, verificando se o aluno já possui dados salvos.
- Valida se o aluno cursou todas as disciplinas do 4º período.
- Permite ao aluno continuar o processo de solicitação mesmo com até 4 disciplinas pendentes.
- Envia um e-mail para a comissão de estágio contendo os dados do aluno e o pedido de estágio.
- Armazena os dados dos alunos em pastas separadas no disco, garantindo persistência entre reinicializações.

---

## **Configuração do Ambiente**

### **Pré-requisitos**
- Python 3.9 ou superior
- Biblioteca `python-telegram-bot`
- Biblioteca `python-dotenv`
- Biblioteca `pdfplumber`

### **Instalação**
1. Clone este repositório:
   ```bash
   git clone https://github.com/TeaH4nd/estagiae_bot.git
   cd estagiae_bot

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
