import re
import pdfplumber


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
