import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)

from lib.email import enviar_email
from lib.pdfReader import handle_pdf
from lib.login import (
    BASE_DIR,
    load_user_data,
    get_user_dir,
)

from dotenv import load_dotenv

# Carregar o token do arquivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Sessões dos usuários
user_sessions = {}


async def start(update: Update, context: CallbackContext) -> None:
    """Inicia a interação com o bot."""
    user_id = str(update.effective_user.id)
    user_dir = get_user_dir(user_id)

    # Verificar se o usuário já tem dados salvos
    if os.path.exists(user_dir):
        dados = load_user_data(user_id)
        nome = dados.get("nome_civil", "Usuário").split()[0]
        await update.message.reply_text(
            f"Olá, {nome}! O que você gostaria de fazer?\n"
            f"1️⃣ /dados - Ver os dados salvos\n"
            f"2️⃣ Enviar um novo boletim em PDF"
        )
    else:
        os.makedirs(user_dir)
        await update.message.reply_text(
            "Olá! Eu sou o Estagiaê 🤖, o robozinho que irá te ajudar com o seu processo de"
            "estágio. Eu sou capaz de extrair informações de boletins acadêmicos em "
            "PDF e te ajudar a organizar esses dados. \n\n"
            "Para começar:\n"
            "1️⃣ Envie um arquivo PDF com o boletim acadêmico.\n"
            "2️⃣ Eu irei processar o documento e extrair as informações principais.\n"
            "3️⃣ Use /dados para ver os dados extraídos.\n"
        )


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


# Handler para as respostas do usuário
async def handle_resposta(update: Update, context: CallbackContext) -> None:
    """Manipula as respostas do usuário à validação de matérias."""
    query = update.callback_query
    await query.answer()

    if query.data == "continuar":
        user_id = str(update.effective_user.id)
        dados = load_user_data(user_id)
        await enviar_email(query, dados)
        await query.edit_message_text("Você optou por continuar mesmo com as matérias faltantes.")
        # Adicione aqui o que deve ser feito em seguida
    elif query.data == "cancelar":
        await query.edit_message_text("Você optou por não continuar.")


def main():
    """Configura o bot e inicia o polling."""
    # Função para garantir que o diretório base exista
    os.makedirs(BASE_DIR, exist_ok=True)

    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("dados", get_user_data))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(CallbackQueryHandler(handle_resposta))

    # Mensagem de boas-vindas
    app.add_handler(MessageHandler(filters.ALL, start))

    # Inicia o bot
    print("Bot está rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
