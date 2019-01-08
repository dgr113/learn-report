# coding: utf-8

import io
import sys
import smtplib
import numpy as np
import pandas as pd
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




def create_report(
        X: pd.DataFrame,
        X_colors_mask: Union[pd.DataFrame, None] = None,
        output_format: str = 'pdf'

) -> bytes:

    """ Сформировать отчет

        https://stackoverflow.com/questions/9622163/save-plot-to-image-file-instead-of-displaying-it-using-matplotlib
    """

    fig, ax = plt.subplots()

    ### Скрыть оси
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    ### Сформировать таблицу
    ax.table(cellText=X.values, cellColours=X_colors_mask, colLabels=X.columns, loc='center')

    ### Записать отчет в файловый поток
    with io.BytesIO() as f:
        plt.savefig(fname=f, figure=fig, format=output_format)
        plt.close(fig)

        result = f.getvalue()
        return result




def send_report_email(
        *reports,
        host: str,
        port: Union[int, str],
        username: str,
        password: str,
        send_from: str,
        send_to: List[str],
        verbose_mode: bool = False,

) -> None:

    """ Отправить отчет с вложением """

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ', '.join(send_to)
    msg['Subject'] = 'Test report from service'
    msg.attach(MIMEText('Test message'))

    for n, report in enumerate(reports, start=1):
        filename = 'report_{}.pdf'.format(str(n))
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

    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()




def get_test_set() -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """ Тестовый набор данных для отчета """

    results = []

    for i in range(3):
        X = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]})
        y = np.array([1, 2, 2, 3])

        color_mapping = {1: 'green', 2: 'red'}
        colors_mask = get_axis_color_mask(X, y, color_mapping=color_mapping)
        metainfo = [
            {'original': '', 'analized': ''},
            {'original': '', 'analized': ''},
        ]

        results.append((X, colors_mask))

    return results





if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default='smtp.yandex.com', type=str)
    parser.add_argument('-port', '--port', default=465, type=int)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-f', '--from-addr', dest='from_addr', type=str)
    parser.add_argument('-t', '--to-addr', dest='to_addr', type=str)

    args = parser.parse_args()
    user_name = args.username or input('Логин: ')
    user_pass = args.password or getpass('Пароль: ')


    with Pool() as pool:
        reports = pool.starmap(
            partial(create_report, output_format='pdf'),
            get_test_set()
        )

        send_report_email(
            *reports,
            host=args.host,
            port=args.port,
            username=user_name,
            password=user_pass,
            send_from=args.from_addr,
            send_to=[args.to_addr]
        )
