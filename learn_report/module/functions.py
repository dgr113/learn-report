# coding: utf-8

import io
import sys
import smtplib
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from functools import partial
from itertools import repeat
from typing import Union, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from more_itertools import always_iterable, collapse
from helpful_vectors.functions import get_consecutive_segments
from learn_report.module.data_structs import TableDesc
from learn_report.module.type_hints import MAIL_ADDRESSES_TYPE, STYLES_LIST_TYPE, TABLE_MASK_TYPE, VECTORIZED_ARRAY_TYPE




def get_axis_color_mask(
        X: pd.DataFrame,
        y: VECTORIZED_ARRAY_TYPE,
        axis: int = 0,
        color_mapping: Union[dict, None] = None,
        default_color: str = 'gray'

) -> pd.DataFrame:

    """ Сформировать маску цветок строк/столбцов для фрейма данных """

    if not color_mapping:
        color_mapping = {1: 'green', 2: 'red'}

    ### Обработка неучтенных в <color_mapping> меток - назначим их цвет как <default_color>
    unsigned_labels = set(y) - set(color_mapping.keys())
    unsigned_color_mapping = dict(zip(unsigned_labels, repeat(default_color)))
    color_mapping.update(unsigned_color_mapping)

    X_mask = X.copy()
    for label, color in color_mapping.items():
        if axis == 0:
            X_mask.iloc[(y == label), :] = color
        else:
            X_mask.iloc[:, (y == label)] = color

    return X_mask.values




def _get_box_coords(x, start_col: int = 0, end_col: int = 1) -> List[Tuple[int, int]]:
    """ Получить координаты левой верхней и правой нижней точки прямоугольной области """

    results = list(zip(
        [start_col, end_col],
        np.percentile(x, [0, 100]).astype(int)
    ))

    return results




def get_styles_list_from_mask(mask: TABLE_MASK_TYPE, style_names: str = 'BACKGROUND') -> STYLES_LIST_TYPE:
    """ Получить список стилей из маски """

    if not mask.empty and mask is not None:
        start_col = 0
        end_col = mask.shape[1]

        ### Формирование измененного фрейма данных
        indexes_by_colors = get_consecutive_segments(mask)
        colors_boundary_coord = indexes_by_colors.apply(partial(_get_box_coords, start_col=start_col, end_col=end_col))

        ### Переиндексация до нужного порядка
        colors_boundary_coord = colors_boundary_coord.reset_index(level=0)
        non_index_columns = colors_boundary_coord.columns.difference([0]).tolist()
        colors_boundary_coord = colors_boundary_coord.reindex(columns=non_index_columns + [0])

        ### Сплющивание массивов
        results = [
            [style_names] + list(collapse(row, levels=1))
            for row in colors_boundary_coord.values.tolist()
        ]
    else:
        results = []

    return results




# noinspection PyUnusedLocal
def build_report(
        *tables_desc: TableDesc,
        output_format: str = 'pdf',
        dpi: int = 300

) -> bytes:

    """ Сформировать отчет

        https://stackoverflow.com/questions/9622163/save-plot-to-image-file-instead-of-displaying-it-using-matplotlib

        :param tables_desc: Описания таблиц для отчета
        :param output_format: Формат отчета
        :param dpi: DPI
    """

    with io.BytesIO() as buffer:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=18
        )

        doc.pagesize = landscape(A4)
        elements = []

        ### Заполняем каждую область своей таблицей из <tables_desc>
        ### обрабатываем возможность 1 (не итерируемой оси), в случае если <tables_desc> состоит из одного элемента
        for n, table_desc in enumerate(tables_desc):
            ### Сформировать таблицу из ее описания
            ### обрабатываем возможность получения одиночного <DataFrame>
            ext_styles = get_styles_list_from_mask(table_desc.mask)
            styles = TableStyle([
                ('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                ('VALIGN', (0, 0), (0, -1), 'TOP'),
                ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                *ext_styles
            ])

            t = Table(table_desc.data.values.tolist())
            t.setStyle(styles)
            elements.append(t)


        doc.build(elements)
        return buffer.getvalue()




# noinspection PyShadowingNames
def send_report_email(
        *reports,
        host: str,
        port: int,
        username: str,
        password: str,
        send_from: str,
        send_to: MAIL_ADDRESSES_TYPE,
        report_format: str,
        verbose_mode: bool = False,

) -> None:

    """ Отправить отчет с вложением """

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ', '.join(always_iterable(send_to))
    msg['Subject'] = 'Test report from service'
    msg.attach(MIMEText('Test message'))

    for n, report in enumerate(reports, start=1):
        filename = 'report_{0}.{1}'.format(str(n), report_format)
        attachedfile = MIMEApplication(report)
        attachedfile.add_header('content-disposition', 'attachment', filename=filename)
        msg.attach(attachedfile)

    smtp = smtplib.SMTP_SSL(host, port)
    if verbose_mode:
        smtp.set_debuglevel(1)

    try:
        smtp.ehlo()
        smtp.starttls()
    except smtplib.SMTPNotSupportedError:
        if verbose_mode:
            print('Warning! Mail server not supported TTLS', file=sys.stderr)

    try:
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())

    except smtplib.SMTPAuthenticationError:
        print('Auth failed!', file=sys.stderr)
    except smtplib.SMTPSenderRefused:
        print('Sender address rejected: not owned by auth user!', file=sys.stderr)
    except Exception:
        print('Unexpected error!', file=sys.stderr)
    finally:
        smtp.close()