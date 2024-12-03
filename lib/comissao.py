from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from lib.consts.comissaoId import COMISSAO
from lib.login import get_alunos, load_user_data, load_user_data_from_dre, save_user_data


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if str(user_id) not in COMISSAO:
            print(f"Uso restrito para a comissão: {user_id}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def get_alunos_pendentes(update: Update, context: CallbackContext):
    alunos = get_alunos()

    if not alunos:
        await update.message.reply_text(
            "_Nenhum aluno encontrado._", parse_mode="Markdown"
        )
        return

    mensagem = "*Estado de Todos os Alunos*\n\n"
    for aluno in alunos:
        nome = aluno["nome_civil"]
        dre = aluno["dre"]
        status = aluno["status"]

        # Adicionar o aluno formatado na mensagem
        if status == "Pendente":
            mensagem += (
                f"• *Nome:* {nome}\n"
                f"  *DRE:* {dre}\n"
                f"  *Status:* `{status}`\n\n"
            )

    await update.message.reply_text(mensagem, parse_mode="Markdown")

@restricted
async def get_aluno_status(update: Update, context: CallbackContext):
    user_id = update.message.text.split()[1]
    print(user_id)
    dados = load_user_data_from_dre(user_id)

    mensagem = (
        f"Nome do Aluno: {dados.get("nome_civil", "Desconhecido")}\n"
        f"DRE: {dados.get("dre", "Desconhecido")}\n"
        f"Email: {dados.get("email", "Desconhecido")}\n"
        f"CR Acumulado: {dados.get("cr_acumulado", "N/A")}\n"
        f"Status do Pedido: {dados.get("status", "Desconhecido")}\n"
    )

    await update.message.reply_text(mensagem, parse_mode="Markdown")

@restricted
async def approve_aluno(update: Update, context: CallbackContext):
    user_id = update.message.text.split()[1]
    dados = load_user_data_from_dre(user_id)
    dados["status"] = "Aprovado"
    save_user_data(dados["telegram_id"], dados)

    mensagem = (
        f"Nome do Aluno: {dados.get("nome_civil", "Desconhecido")}\n"
        f"DRE: {dados.get("dre", "Desconhecido")}\n"
        "Pedido de estágio aprovado!\n\n"
        "Irei enviar uma mensagem para o aluno ficar ciente."
    )
    await update.message.reply_text(mensagem)
    await send_user_message(update, context, user_id)

@restricted
async def reject_aluno(update: Update, context: CallbackContext):
    user_id = update.message.text.split()[1]
    dados = load_user_data_from_dre(user_id)
    dados["status"] = "Rejeitado"
    save_user_data(dados["telegram_id"], dados)

    mensagem = (
        f"Nome do Aluno: {dados.get("nome_civil", "Desconhecido")}\n"
        f"DRE: {dados.get("dre", "Desconhecido")}\n"
        "Pedido de estágio rejeitado!\n\n"
        "Irei enviar uma mensagem para o aluno ficar ciente."
    )
    await update.message.reply_text(mensagem)
    await send_user_message(update, context, user_id)

async def send_user_message(update: Update, context: CallbackContext, user_id):
    dados = load_user_data_from_dre(user_id)
    email = dados.get("email", "Desconhecido")
    status = dados.get("status", "Desconhecido")

    if email == "Desconhecido":
        await update.message.reply_text("Usuário sem e-mail cadastrado.")
        return

    if status == "Aprovado":
        mensagem = (
            "🎉 *Parabéns!* 🎉\n\n"
            "Seu pedido foi *aprovado com sucesso*! 🚀\n"
            "Fique de olho em seu e-mail para mais informações. "
            "Estamos felizes em ajudar você a dar mais um passo em sua jornada! 😊",
        )
    elif status == "Rejeitado":
        mensagem = (
            "😔 *Que pena!* 😔\n\n"
            "Infelizmente, seu pedido não pôde ser aprovado desta vez. 😢\n"
            "Recomendamos verificar os requisitos pendentes e tentar novamente. "
            "Estamos aqui para ajudar você no que for necessário! 💪",
        )
    else:
        mensagem = "Seu pedido de estágio está pendente."

    await context.bot.send_message(chat_id=int(dados["telegram_id"]), text=mensagem, parse_mode="Markdown")