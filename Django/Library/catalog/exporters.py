"""Funções que transformam uma tabela (cabeçalho + linhas) em arquivo para download.

Todas recebem os mesmos argumentos (filename, title, headers, rows) e devolvem
uma HttpResponse pronta. São usadas pela exportação do acervo e pelos relatórios.
"""

import csv  # módulo do Python para escrever arquivos CSV

from django.http import HttpResponse
from django.utils import timezone


def csv_response(filename, title, headers, rows):
    """CSV separado por ';' (o Excel em português abre direto).

    O parâmetro title não é usado aqui, mas existe para que as três funções
    tenham exatamente a mesma assinatura.
    """
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    # attachment: o navegador baixa o arquivo em vez de mostrar na tela
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")  # "BOM": faz o Excel reconhecer os acentos
    writer = csv.writer(response, delimiter=";")  # a resposta funciona como um arquivo aberto
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def xlsx_response(filename, title, headers, rows):
    """Planilha Excel (.xlsx) com cabeçalho em negrito."""
    # Importados aqui dentro: a biblioteca só é carregada quando alguém pede um Excel
    from openpyxl import Workbook
    from openpyxl.styles import Font

    workbook = Workbook()
    sheet = workbook.active  # a primeira aba da planilha
    sheet.title = title[:31]  # o Excel não aceita nomes de aba com mais de 31 caracteres
    sheet.append(headers)
    for cell in sheet[1]:  # sheet[1] é a primeira linha (o cabeçalho)
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append(row)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    workbook.save(response)  # grava a planilha direto na resposta
    return response


def pdf_response(filename, title, headers, rows):
    """PDF com título, data de geração e uma tabela listrada."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'

    # Documento A4 deitado (landscape): tabelas largas cabem melhor
    document = SimpleDocTemplate(response, pagesize=landscape(A4), title=title)
    styles = getSampleStyleSheet()  # estilos de texto prontos (Title, Normal...)

    # A tabela recebe uma lista de listas; a primeira linha é o cabeçalho.
    # repeatRows=1 repete o cabeçalho no topo de cada página nova.
    table = Table([headers] + [[str(value) for value in row] for row in rows], repeatRows=1)
    # Coordenadas no formato (coluna, linha); -1 significa "a última"
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),  # fundo escuro no cabeçalho
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # texto branco no cabeçalho
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # cabeçalho em negrito
                ("FONTSIZE", (0, 0), (-1, -1), 9),  # fonte 9 na tabela inteira
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),  # linhas de grade
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),  # linhas listradas
            ]
        )
    )

    generated_at = timezone.localtime().strftime("%d/%m/%Y %H:%M")
    # build monta o documento a partir de uma lista de blocos, de cima para baixo
    document.build(
        [
            Paragraph(title, styles["Title"]),
            Paragraph(f"Gerado em {generated_at}", styles["Normal"]),
            Spacer(1, 12),  # espaço em branco de 12 pontos
            table,
        ]
    )
    return response


# Formato pedido na URL -> função que gera o arquivo
EXPORTERS = {
    "csv": csv_response,
    "xlsx": xlsx_response,
    "pdf": pdf_response,
}
