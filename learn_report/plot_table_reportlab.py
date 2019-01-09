# coding: utf-8

import pandas as pd
import matplotlib
matplotlib.use('GTK3Cairo')

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from functools import partial




def get_stylized_data(data: pd.DataFrame) -> pd.DataFrame:
    """ Установка стилей и <Paragraph> для каждой ячейки - ОЧЕНЬ МЕДЛЕННО для больших наборов данных! """

    s = getSampleStyleSheet()
    s = s["BodyText"]
    s.wordWrap = 'CJK'

    data = data.applymap(partial(Paragraph, style=s))
    return data




def main():
    doc = SimpleDocTemplate(
        "test_report_lab.pdf",
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18
    )

    doc.pagesize = landscape(A4)
    elements = []


    data = pd.DataFrame([
        ["A", "01", "ABCD", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"]*7,
        ["B", "02", "CDEF", "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"]*7,
        ["B", "02", "CDEF", "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"]*7,
        ["B", "02", "CDEF", "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"]*7
    ]*150)

    style = TableStyle([
        ('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
        ('TEXTCOLOR', (1, 1), (-2, -2), colors.red),
        ('VALIGN', (0, 0), (0, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ])

    # data = get_stylized_data(data)
    t = Table(data.values.tolist())
    t.setStyle(style)

    elements.append(t)
    doc.build(elements)




if __name__ == "__main__":
    main()
