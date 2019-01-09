# coding: utf-8

import io
import sys
import smtplib
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from functools import partial
from multiprocessing import Pool
from getpass import getpass
from itertools import repeat
from typing import Union, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from argparse import ArgumentParser
from more_itertools import always_iterable
matplotlib.use('TkCairo')

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

    ### Области для таблиц
    nrows = len(tables_desc)
    fig, axes_list = plt.subplots(nrows=nrows, ncols=1)

    ### Скрыть оси графика
    fig.patch.set_visible(False)

    ### Заполняем каждую область своей таблицей из <tables_desc>
    ### обрабатываем возможность 1 (не итерируемой оси), в случае если <tables_desc> состоит из одного элемента
    for n, ax in enumerate(always_iterable(axes_list)):
        ax.axis('off')
        ax.axis('off')
        ax.axis('tight')
        ax.axis('tight')

        ### Сформировать таблицу из ее описания
        ### обрабатываем возможность получения одиночного <DataFrame>
        table_desc = tables_desc[n]
        try:
            table, colors = table_desc[0], table_desc[1]
        except (TypeError, ValueError, KeyError):
            table, colors, = table_desc, None

        ax.table(cellText=table.values, cellColours=colors, colLabels=table.columns, loc='upper center')

    # plt.plot()
    # plt.show()

    ### Записать отчет в файловый поток
    with io.BytesIO() as f:
        plt.savefig(fname=f, figure=fig, format=output_format)
        plt.clf()
        plt.close()

        result = f.getvalue()
        return result




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
        'B': [5, 6, 7, 8]*100,
        'C': [5, 6, 7, 8]*100,
        'D': [5, 6, 7, 8]*100,
        'E': [5, 6, 7, 8]*100,
        'F': [5, 6, 7, 8]*100,
    })
    y1 = np.array([1, 2, 2, 3]*100)
    colors_mask1 = get_axis_color_mask(X1, y1, color_mapping={1: 'green', 2: 'red'})


    X2 = pd.DataFrame({'original': [111], 'parsed': [222]})


    results = [
        [(X1, colors_mask1), X2]
    ]*100

    return results





if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default='smtp.yandex.com', type=str)
    parser.add_argument('-port', '--port', default=465, type=int)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-f', '--format', dest='report_format', type=str, default='pdf')
    parser.add_argument('-dpi', '--dpi', type=int, default=300)
    parser.add_argument('-from', '--from-addr', dest='from_addr', type=str, default='dmitry-gr87@yandex.ru')
    parser.add_argument('-to', '--to-addr', dest='to_addr', nargs='*', type=str, default='dmitry-gr87@yandex.ru')

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
