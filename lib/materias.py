from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from lib.email import enviar_email


MATERIAS_4_PERIODO = [
    # 1 periodo
    'ICP131',
    'ICP132',
    'ICP133',
    'ICP134',
    'ICP135',
    'ICP136',
    'ICPX06',
    'ICPZ55',
    # 2 periodo
    'ICP141',
    'ICP142',
    'ICP143',
    'ICP144',
    'ICP145',
    'MAE111',
    # 3 periodo
    'ICP115',
    'ICP116',
    'ICP237',
    'ICP238',
    'ICP239',
    'MAE992',
    # 4 periodo
    'ICP246',
    'ICP248',
    'ICP249',
    'ICP489',
    'MAD243',
]

async def validate_materias(update: Update, context: CallbackContext, dados) -> None:
    """Valida as matérias do 4º período."""
    materias = dados.get("codigos_disciplinas", [])

    if not materias:
        await update.message.reply_text("Nenhuma matéria cadastrada pelo aluno.")
        return

    # Verificar quais matérias do 4º período não foram cursadas
    materias_faltantes = list(set(MATERIAS_4_PERIODO) - set(materias))

    if not materias_faltantes:
        await enviar_email(update, dados)
        await update.message.reply_text(
            "Você já cursou todas as matérias do 4º período." +
            "Vou enviar um email para a comissao de estagio com os seus dados!"
            )
        return

    if len(materias_faltantes) <= 4:
        # Perguntar ao usuário se ele deseja continuar
        keyboard = [
            [
                InlineKeyboardButton("Sim", callback_data="continuar"),
                InlineKeyboardButton("Não", callback_data="cancelar"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        materias_faltantes_str = ", ".join(materias_faltantes)
        await update.message.reply_text(
            f"Você ainda não cursou as seguintes matérias do 4º período: {
                materias_faltantes_str}.\n"
            "Deseja continuar mesmo assim?",
            reply_markup=reply_markup,
        )
        return

    # Caso o usuário tenha mais de 4 matérias faltantes
    await update.message.reply_text(
        f"Você ainda não cursou as seguintes matérias do 4º período: {
            ', '.join(materias_faltantes)}.\n"
        "Não é possível continuar enquanto você não cursar mais matérias."
    )
