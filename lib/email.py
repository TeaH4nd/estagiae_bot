from email.mime.text import MIMEText
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from telegram import Update

# Configurações de e-mail
SMTP_SERVER = "smtp.gmail.com"  # Servidor SMTP (exemplo: Gmail)
SMTP_PORT = 587  # Porta SMTP para TLS
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")  # Endereço de e-mail remetente
EMAIL_SENHA = os.getenv("EMAIL_SENHA")  # Senha do e-mail
EMAIL_DESTINATARIO = "comissao.estagio@universidade.com"  # E-mail da comissão de estágio


async def enviar_email(update: Update, dados) -> None:
    """Envia um e-mail com os dados do aluno para a comissão de estágio."""
    try:
        # Configuração da mensagem
        nome = dados.get("nome_civil", "Desconhecido")
        registro = dados.get("registro", "Desconhecido")
        cr_acumulado = dados.get("cr_acumulado", "N/A")
        disciplinas = ", ".join(dados.get("codigos_disciplinas", []))

        subject = "Pedido de Estágio"
        body = (
            f"Nome do Aluno: {nome}\n"
            f"Registro: {registro}\n"
            f"CR Acumulado: {cr_acumulado}\n"
            f"Disciplinas Cursadas: {disciplinas}\n"
            "\nSolicitação de autorização para estágio."
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
            server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, message.as_string())

        await update.message.reply_text("E-mail enviado com sucesso para a comissão de estágio.")
    except Exception as e:
        await update.message.reply_text(f"Erro ao enviar o e-mail: {e}")
