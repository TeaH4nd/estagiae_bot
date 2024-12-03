from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from lib.email import enviar_email
from lib.login import load_user_data, save_user_data


BYPASS_VALIDATION = True

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

    if BYPASS_VALIDATION:
        await update.message.reply_text(
            "Você já cursou todas as matérias do 4º período."
        )
        await solicitar_tipo_pedido(update, dados)
        return

    if not materias:
        await update.message.reply_text("Nenhuma matéria cadastrada pelo aluno.")
        return

    # Verificar quais matérias do 4º período não foram cursadas
    materias_faltantes = list(set(MATERIAS_4_PERIODO) - set(materias))

    if not materias_faltantes:
        await solicitar_tipo_pedido(update, dados)
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


async def solicitar_tipo_pedido(update: Update, context: CallbackContext) -> None:
    """Solicita ao usuário o tipo de pedido de estágio."""
    keyboard = [
        [InlineKeyboardButton("Primeiro Estágio", callback_data="pedido_inicio1")],
        [InlineKeyboardButton("Segundo Estágio", callback_data="pedido_inicio2")],
        [InlineKeyboardButton("Terceiro Estágio", callback_data="pedido_inicio3")],
        [InlineKeyboardButton("Renovação de Estágio", callback_data="pedido_renovacao")],
        [InlineKeyboardButton("Finalização de Estágio", callback_data="pedido_finalizacao")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Por favor, escolha o tipo de pedido de estágio que você deseja fazer:",
        reply_markup=reply_markup,
    )

async def handle_tipo_pedido(update: Update, context: CallbackContext) -> None:
    """Lida com a escolha do tipo de pedido de estágio."""
    query = update.callback_query
    await query.answer()

    tipo_pedido = query.data
    user_id = str(update.effective_user.id)
    dados = load_user_data(user_id)

    if tipo_pedido == "pedido_inicio1":
        await query.edit_message_text("Você está solicitando seu Primeiro estágio!")
        dados['tipo_pedido'] = "pedido_inicio1"
    elif tipo_pedido == "pedido_inicio2":
        await query.edit_message_text("Você está solicitando seu Segundo estágio!")
        dados['tipo_pedido'] = "pedido_inicio2"
    elif tipo_pedido == "pedido_inicio3":
        await query.edit_message_text("Você está solicitando seu Terceiro estágio!")
        dados['tipo_pedido'] = "pedido_inicio3"
    elif tipo_pedido == "pedido_renovacao":
        await query.edit_message_text("Você escolheu: Renovação de Estágio.")
        dados['tipo_pedido'] = "pedido_renovacao"
    elif tipo_pedido == "pedido_finalizacao":
        await query.edit_message_text("Você escolheu: Finalização de Estágio.")
        dados['tipo_pedido'] = "pedido_finalizacao"
    else:
        dados['tipo_pedido'] = "Desconhecido"
    save_user_data(user_id, dados)

    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Ok! Vou enviar um email para a comissão de estágio com os seus dados.")
    await enviar_email(update, context, dados)
    
