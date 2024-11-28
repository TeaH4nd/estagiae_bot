from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from telegram.constants import ChatAction
from dotenv import load_dotenv
import os

from lib.pdfReader import extrair_dados_boletim

# Carregar o token do arquivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Sessões dos usuários
user_sessions = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Mensagem inicial do bot."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {}  # Criar uma sessão para o usuário
    await update.message.reply_text("Olá! Envie um arquivo PDF com o boletim para começar.")

async def handle_pdf(update: Update, context: CallbackContext) -> None:
    """Processa o arquivo PDF enviado pelo usuário."""
    user_id = update.effective_user.id

    # Verificar se o arquivo é um PDF
    if update.message.document.mime_type != "application/pdf":
        await update.message.reply_text("Por favor, envie um arquivo PDF.")
        return

    # Baixar o arquivo
    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    file_path = f"{user_id}_boletim.pdf"
    await file.download_to_drive(file_path)

    # Informar o usuário que o arquivo está sendo processado
    await update.message.reply_chat_action(ChatAction.TYPING)

    # Extrair dados do boletim
    try:
        dados = extrair_dados_boletim(file_path)
        user_sessions[user_id] = dados  # Salvar os dados na sessão do usuário

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
    user_id = update.effective_user.id
    if user_id in user_sessions and user_sessions[user_id]:
        dados = user_sessions[user_id]
        resposta = (
            f"**Seus Dados Salvos:**\n"
            f"**Nome Civil:** {dados['nome_civil']}\n"
            f"**DRE:** {dados['dre']}\n"
            f"**CR Acumulado:** {dados['cr_acumulado']}\n"
            f"**Códigos de Disciplinas:** {', '.join(dados['codigos_disciplinas'])}\n"
        )
    else:
        resposta = "Nenhum dado salvo para este usuário."
    await update.message.reply_text(resposta, parse_mode="Markdown")

def main():
    """Configura o bot e inicia o polling."""
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dados", get_user_data))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # Inicia o bot
    print("Bot está rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
