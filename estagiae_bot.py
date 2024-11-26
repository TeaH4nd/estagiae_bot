from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Função para responder ao comando /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Olá! Eu sou um bot. Como posso ajudar?')

# Função para responder a mensagens de texto
async def echo(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    await update.message.reply_text(f'Você disse: {user_message}')

# Função principal
def main():
    if not TOKEN:
        print("Erro: TOKEN não encontrado. Verifique seu arquivo .env.")
        return

    # Inicia o aplicativo do bot
    app = Application.builder().token(TOKEN).build()
    
    # Adiciona os handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Inicia o bot
    print("Bot está rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()
