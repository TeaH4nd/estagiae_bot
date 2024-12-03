import os
import re

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)

from dotenv import load_dotenv

from lib.comissao import (
    approve_aluno,
    get_aluno_status,
    get_alunos_pendentes,
    reject_aluno
)
from lib.consts.comissaoId import COMISSAO
from lib.materias import handle_email, handle_resposta, handle_tipo_pedido
from lib.pdfReader import handle_pdf
from lib.login import (
    ALUNO_DIR,
    BASE_DIR,
    COMISSAO_DIR,
    get_user_data,
    get_user_status,
    load_user_data,
    get_user_dir,
)


# Carregar o token do arquivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: CallbackContext) -> None:
    """Inicia a interação com o bot."""
    user_id = str(update.effective_user.id)
    user_dir = get_user_dir(user_id)

    if re.match(r"^\S+@\S+\.\S+$", update.message.text):
        await handle_email(update, context)
        return

    # Verificar se o usuário já tem dados salvos
    if user_id in COMISSAO:
        await update.message.reply_text(
            "Olá, Comissão de Estágio! O que você gostaria de fazer?\n\n"
            "- Digite /pendentes - Ver alunos aguardando resposta\n"
            "- Digite /aluno <DRE> - Ver a situação de um aluno específico\n"
            "- Digite /aprovar <DRE> - Aprovar um pedido de estágio\n"
            "- Digite /negar <DRE> - Negar um pedido de estágio\n"
        )
    else:
        if os.path.exists(user_dir):
            dados = load_user_data(user_id)
            nome = dados.get("nome_civil", "Usuário").split()[0]
            await update.message.reply_text(
                f"Olá, {nome}! O que você gostaria de fazer?\n\n"
                f"- Digite /dados - Ver os dados salvos\n"
                f"- Digite /status - Ver o status do seu pedido de estágio\n"
                f"- Envie um novo boletim em PDF"
            )
        else:
            os.makedirs(user_dir)
            await update.message.reply_text(
                "Olá! Eu sou o Estagiaê 🤖, o robozinho que irá te ajudar com o seu processo de"
                " estágio. Eu sou capaz de extrair informações de boletins acadêmicos em "
                "PDF e te ajudar a organizar esses dados. \n\n"
                "Para começar, envie um arquivo PDF com o boletim acadêmico, e eu "
                "irei processar o documento e extrair as informações principais.\n\n"
                "- Digite /dados - Ver os dados salvos\n"
                "- Digite /status - Ver o status do seu pedido de estágio\n"
                "- Envie um novo boletim em PDF"
            )


def main():
    """Configura o bot e inicia o polling."""
    # Função para garantir que o diretório base exista
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(ALUNO_DIR, exist_ok=True)
    os.makedirs(COMISSAO_DIR, exist_ok=True)

    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("dados", get_user_data))
    app.add_handler(CommandHandler("status", get_user_status))
    app.add_handler(CommandHandler("pendentes", get_alunos_pendentes))
    app.add_handler(CommandHandler("aluno", get_aluno_status))
    app.add_handler(CommandHandler("aprovar", approve_aluno))
    app.add_handler(CommandHandler("negar", reject_aluno))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # CallbackQueryHandler para os tipos de pedidos
    app.add_handler(CallbackQueryHandler(
        handle_tipo_pedido, pattern=r"^pedido_"))

    # CallbackQueryHandler para confirmações
    app.add_handler(CallbackQueryHandler(
        handle_resposta, pattern=r"^confirmar_|^cancelar_"))

    # Mensagem de boas-vindas
    app.add_handler(MessageHandler(filters.ALL, start))

    # Inicia o bot
    print("Bot está rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
