# coding: utf-8

import sys
import json
import types
import pandas as pd
from typing import List
from jsonschema import Draft4Validator
from argparse import ArgumentParser
from functools import partial
from getpass import getpass
from multiprocessing.pool import Pool
from learn_report.module.data_structs import TableDesc
from learn_report.module.functions import build_report, send_report_email
from learn_report.module.settings import SCHEMA_MAPPING, THREAD_WORKERS_COUNT
from learn_report.module.tests import get_test_set




def reports_data_converter(reports: List[List[dict]]) -> List[List[TableDesc]]:
    """ Приведение типов """

    results = [
        [
            TableDesc(pd.DataFrame(table_desc['data']), pd.DataFrame(table_desc['mask']))
            for table_desc in report
        ]
        for report in reports
    ]

    return results



def dataclass_pickle_prepair(*classes) -> None:
    """ Подготовка некоторых классов для сериализации (namedtuple, dataclass)

        :type classes: объекты классов
    """

    for cls in classes:
        setattr(types, cls.__name__, cls)



def main():
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default='smtp.yandex.com', type=str)
    parser.add_argument('-port', '--port', default=465, type=int)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-f', '--format', dest='report_format', type=str, default='pdf')
    parser.add_argument('-dpi', '--dpi', type=int, default=300)
    parser.add_argument('-from', '--from-addr', dest='from_addr', type=str, default='')
    parser.add_argument('-to', '--to-addr', dest='to_addr', nargs='*', type=str, default='')
    parser.add_argument('-s', '--sources', dest='sources', nargs='?', help='Sources from json')
    parser.add_argument('-test', '--test-mode', dest='test_mode', action='store_true', default=True)

    args = parser.parse_args()
    user_name = args.username or input('Логин: ')
    user_pass = args.password or getpass('Пароль: ')


    with open(SCHEMA_MAPPING['get'], 'r') as f:
        if args.test_mode:
            sources = get_test_set(as_json=True)
        else:
            sources = args.sources or sys.stdin.read().strip()

        schema = json.load(f)
        validator = Draft4Validator(schema)
        data = json.loads(sources)
        validator.validate(data)


        dataclass_pickle_prepair(TableDesc)
        with Pool(THREAD_WORKERS_COUNT) as pool:
            reports = pool.starmap(
                partial(build_report, output_format=args.report_format, dpi=args.dpi),
                reports_data_converter(data['data'])
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




if __name__ == "__main__":
    main()
