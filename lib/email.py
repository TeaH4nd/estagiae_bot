import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update
from telegram.ext import CallbackContext
from dotenv import load_dotenv

from lib.login import load_user_data

load_dotenv()
# Configurações de e-mail
SMTP_SERVER = "smtp.gmail.com"  # Servidor SMTP (exemplo: Gmail)
SMTP_PORT = 587  # Porta SMTP para TLS
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")  # Endereço de e-mail remetente
EMAIL_SENHA = os.getenv("EMAIL_SENHA")  # Senha do e-mail
# E-mail da comissão de estágio
EMAIL_DESTINATARIO = "danielal@dcc.ufrj.br"


async def enviar_email(update: Update, context: CallbackContext, dados) -> None:
    """Envia um e-mail com os dados do aluno para a comissão de estágio."""
    try:
        user_id = str(update.effective_user.id)
        dados = load_user_data(user_id)

        # Configuração da mensagem
        nome = dados.get("nome_civil", "Desconhecido")
        dre = dados.get("dre", "Desconhecido")
        cr_acumulado = dados.get("cr_acumulado", "N/A")
        pedido = dados.get("tipo_pedido", "Desconhecido")
        email_aluno = dados.get("email", "Desconhecido")
        disciplinas = dados.get("disciplinas_faltantes", [])
        disciplinas = ", ".join(disciplinas) if disciplinas else "N/A"
        
        # Frases específicas para cada tipo de pedido
        frases_pedido = {
            "pedido_inicio1": "Solicitação para o primeiro estágio.",
            "pedido_inicio2": "Solicitação para o segundo estágio.",
            "pedido_inicio3": "Solicitação para o terceiro estágio.",
            "pedido_renovacao": "Solicitação de renovação do estágio atual.",
            "pedido_finalizacao": "Solicitação de finalização do estágio."
        }

        # Obter a frase específica
        frase_pedido = frases_pedido.get(pedido, "Tipo de pedido não reconhecido.")

        subject = "Pedido de Estágio"
        body = (
            f"Nome do Aluno: {nome}\n"
            f"DRE: {dre}\n"
            f"Email: {email_aluno}\n"
            f"CR Acumulado: {cr_acumulado}\n"
            f"Disciplinas do 4 periodo que falta cursar: {disciplinas}\n\n"
            f"{frase_pedido}\n\n"
        )

        message = MIMEMultipart()
        message["From"] = EMAIL_REMETENTE
        message["To"] = EMAIL_DESTINATARIO
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Envio do e-mail
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO,
                            message.as_string())

        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text="E-mail enviado com sucesso para a comissão de estágio!")
        await context.bot.send_message(chat_id=chat_id, text="Fique no aguardo para o contato da comissão.")

    except Exception as e:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text=f"Erro ao enviar o e-mail: {e}")