import re
import pdfplumber


def extrair_dados_boletim(pdf_path):
    """Extrai dados do boletim a partir de um arquivo PDF."""
    dados = {
        "nome_civil": None,
        "dre": None,
        "codigos_disciplinas": [],
        "cr_acumulado": None
    }
    
    # Abrir o arquivo PDF
    with pdfplumber.open(pdf_path) as pdf:
        total_paginas = len(pdf.pages)
        for index, pagina in enumerate(pdf.pages):
            texto = pagina.extract_text()

            # Procurar Nome Civil e Registro
            if not dados["nome_civil"] or not dados["dre"]:
                match_nome_registro = re.search(r"Nome Civil\s+([A-Z\s]+)\s+\d{11}\s+\d{2}/\d{2}/\d{4}\s+(\d{9})", texto, re.DOTALL)
                if match_nome_registro:
                    dados["nome_civil"] = match_nome_registro.group(1).strip()
                    dados["dre"] = match_nome_registro.group(2).strip()

            # Procurar Códigos de Disciplinas (Formato XXX999)
            codigos = re.findall(r"\b[A-Z]{3}\d{3}\b", texto)
            dados["codigos_disciplinas"].extend(codigos)

            # Processar apenas a última página para o CR acumulado
            if index == total_paginas - 1:
                match_cr = re.findall(r"acumulado\s+\.*\s+(?:[\d.,]+\s+){4}([\d.]+)", texto)
                if match_cr:
                    dados["cr_acumulado"] = match_cr[-1]

    # Remover duplicatas nos códigos de disciplinas
    dados["codigos_disciplinas"] = list(set(dados["codigos_disciplinas"]))
    
    return dados