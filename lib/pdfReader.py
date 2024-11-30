import os
import re
import pdfplumber
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ChatAction

from lib.materias import validate_materias
from lib.login import get_user_dir, save_user_data


# Função para extrair dados do boletim
def extrair_dados_boletim(pdf_path):
    """Extrai dados do boletim a partir de um arquivo PDF."""
    dados = {
        "nome_civil": None,
        "dre": None,
        "codigos_disciplinas": [],
        "cr_acumulado": None,
    }

    with pdfplumber.open(pdf_path) as pdf:
        total_paginas = len(pdf.pages)
        for index, pagina in enumerate(pdf.pages):
            texto = pagina.extract_text()

            # Nome Civil e Registro
            if not dados["nome_civil"] or not dados["dre"]:
                match_nome_registro = re.search(
                    r"Nome Civil\s+([A-Z\s]+)\s+\d{11}\s+\d{2}/\d{2}/\d{4}\s+(\d{9})",
                    texto,
                    re.DOTALL,
                )
                if match_nome_registro:
                    dados["nome_civil"] = match_nome_registro.group(1).strip()
                    dados["dre"] = match_nome_registro.group(2).strip()

            # Códigos de Disciplinas
            codigos = re.findall(r"\b[A-Z]{3}\d{3}\b", texto)
            dados["codigos_disciplinas"].extend(codigos)

            # CR Acumulado
            if index == total_paginas - 1:
                match_cr = re.search(
                    r"acumulado\s+\.*\s+(?:[\d.,]+\s+){4}([\d.]+)", texto
                )
                if match_cr:
                    dados["cr_acumulado"] = match_cr.group(1).strip()

    dados["codigos_disciplinas"] = list(set(dados["codigos_disciplinas"]))
    return dados

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
            f"**Códigos de Disciplinas:** {
                ', '.join(dados['codigos_disciplinas'])}\n"
        )
        await update.message.reply_text(resposta, parse_mode="Markdown")
        await validate_materias(update, context, dados)

    except Exception as e:
        await update.message.reply_text(f"Erro ao processar o PDF: {e}")
