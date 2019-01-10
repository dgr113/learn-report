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
from multiprocessing import Pool
from getpass import getpass
from itertools import repeat
from typing import Union, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from argparse import ArgumentParser
from more_itertools import always_iterable, collapse
from helpful_vectors.functions import get_consecutive_segments

VECTORIZED_ARRAY_TYPE = Union[np.array, pd.Series]




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




def get_styles_list_from_mask(mask: pd.DataFrame, style_names: str = 'BACKGROUND') -> List[list]:
    """ Получить список стилей из маски """

    start_col = 0
    end_col = mask.shape[1]

    ### Формирование измененного фрейма данных
    indexes_by_colors = get_consecutive_segments(mask)
    colors_boundary_coord = indexes_by_colors.apply(
        lambda x: list(zip(
            [start_col, end_col],
            np.percentile(x, [0, 100]).astype(int)
        ))
    )

    ### Переиндексация до нужного порядка
    colors_boundary_coord = colors_boundary_coord.reset_index(level=0)
    non_index_columns = colors_boundary_coord.columns.difference([0]).tolist()
    colors_boundary_coord = colors_boundary_coord.reindex(columns=non_index_columns + [0])

    ### Сплющивание массивов
    results = [
        [style_names] + list(collapse(row, levels=1))
        for row in colors_boundary_coord.values.tolist()
    ]

    return results




def build_report(
        *tables_desc: Tuple[pd.DataFrame, Union[pd.DataFrame, None]],
        output_format: str = 'pdf',
        dpi: int = 300

) -> bytes:

    """ Сформировать отчет

        https://stackoverflow.com/questions/9622163/save-plot-to-image-file-instead-of-displaying-it-using-matplotlib

        :param tables_desc: Описания таблиц для отчета вида [(<таблица>, <цвета>), ...]
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
            try:
                table, colors_mask = table_desc[0], table_desc[1]
            except (TypeError, ValueError, KeyError):
                table, colors_mask, = table_desc, None

            ext_styles = get_styles_list_from_mask(colors_mask) if colors_mask is not None else []
            styles = TableStyle([
                ('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                ('VALIGN', (0, 0), (0, -1), 'TOP'),
                ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                *ext_styles
            ])

            t = Table(table.values.tolist())
            t.setStyle(styles)
            elements.append(t)


        doc.build(elements)
        return buffer.getvalue()







def send_report_email(
        *reports,
        host: str,
        port: Union[int, str],
        username: str,
        password: str,
        send_from: str,
        send_to: Union[str, List[str]],
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
        smtp.close()
    except smtplib.SMTPAuthenticationError:
        print('Auth failed!', file=sys.stderr)
    except Exception:
        print('Unexpected error!', file=sys.stderr)

    finally:
        smtp.close()








def _get_test_set():
    """ Тестовый набор данных для отчета """

    X1 = pd.DataFrame({
        'A': [1, 2, 3, 4]*100,
        'B': [1, 2, 3, 4]*100,
        'C': [1, 2, 3, 4]*100,
    })
    y1 = np.array([1]*4 + [2, 2, 2, 2]*99)
    colors_mask1 = get_axis_color_mask(X1, y1, color_mapping={1: 'green', 2: 'red'})

    # X2 = pd.DataFrame({'original': [111], 'parsed': [222]})

    results = [
        [(X1, colors_mask1)]
    ]*4

    return results





if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default='smtp.yandex.com', type=str)
    parser.add_argument('-port', '--port', default=465, type=int)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-f', '--format', dest='report_format', type=str, default='pdf')
    parser.add_argument('-dpi', '--dpi', type=int, default=300)
    parser.add_argument('-from', '--from-addr', dest='from_addr', type=str, default='')
    parser.add_argument('-to', '--to-addr', dest='to_addr', nargs='*', type=str, default='')

    args = parser.parse_args()
    user_name = args.username or input('Логин: ')
    user_pass = args.password or getpass('Пароль: ')


    with Pool() as pool:
        reports = pool.starmap(
            partial(build_report, output_format=args.report_format, dpi=args.dpi),
            _get_test_set()
        )

        send_report_email(
            *reports,
            host=args.host,
            port=args.port,
            username=user_name,
            password=user_pass,
            send_from=args.from_addr,
            send_to=args.to_addr,
            report_format=args.report_format
        )
