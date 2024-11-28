import os
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

from lib.pdfReader import extrair_dados_boletim
from lib.login import (
    BASE_DIR,
    load_user_data,
    get_user_dir,
    save_user_data,
)

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

async def handle_pdf(update: Update, context: CallbackContext) -> None:
    """Processa o arquivo PDF enviado pelo usuário."""
    user_id = str(update.effective_user.id)
    user_dir = get_user_dir(user_id)

    # Verificar se o arquivo é um PDF
    if update.message.document.mime_type != "application/pdf":
        await update.message.reply_text("Por favor, envie um arquivo PDF.")
        return

    # Baixar o arquivo
    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    pdf_path = os.path.join(user_dir, "boletim.pdf")
    await file.download_to_drive(pdf_path)

    # Informar o usuário que o arquivo está sendo processado
    await update.message.reply_chat_action(ChatAction.TYPING)

    # Extrair dados do boletim
    try:
        dados = extrair_dados_boletim(pdf_path)
        save_user_data(user_id, dados)

        # Responder com os dados extraídos
        resposta = (
            f"**Dados Extraídos:**\n"
            f"**Nome Civil:** {dados['nome_civil']}\n"
            f"**DRE:** {dados['dre']}\n"
            f"**CR Acumulado:** {dados['cr_acumulado']}\n"
            f"**Códigos de Disciplinas:** {', '.join(dados['codigos_disciplinas'])}\n"
        )
        await update.message.reply_text(resposta, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Erro ao processar o PDF: {e}")


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
            f"**Códigos de Disciplinas:** {', '.join(dados['codigos_disciplinas'])}\n"
        )
    else:
        resposta = "Nenhum dado salvo para este usuário. Envie um boletim em PDF para começar."
    await update.message.reply_text(resposta, parse_mode="Markdown")

def main():
    """Configura o bot e inicia o polling."""
    # Função para garantir que o diretório base exista
    os.makedirs(BASE_DIR, exist_ok=True)

    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("dados", get_user_data))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # Mensagem de boas-vindas
    app.add_handler(MessageHandler(filters.ALL, start))

    # Inicia o bot
    print("Bot está rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
