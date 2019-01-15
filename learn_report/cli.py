# coding: utf-8

import sys
import json
from asyncio import create_task, run as run_async
from concurrent.futures.process import ProcessPoolExecutor
from jsonschema import Draft4Validator
from argparse import ArgumentParser
from getpass import getpass
from learn_report.module.functions import start_async
from learn_report.settings import SCHEMA_MAPPING, THREAD_WORKERS_COUNT
from learn_report.module.tests import get_test_set






async def func(executor):
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default='smtp.yandex.com', type=str)
    parser.add_argument('-port', '--port', default=465, type=int)
    parser.add_argument('-u', '--username', type=str, default='')
    parser.add_argument('-p', '--password', type=str, default='')
    parser.add_argument('-width', '--width', dest='report_width', type=int, default=210, help='Report width in millimeters')
    parser.add_argument('-height', '--height', dest='report_height', type=int, default=297, help='Report height in millimeters')
    parser.add_argument('-ps', '--process-count', dest='process_count', type=int, default=THREAD_WORKERS_COUNT)
    parser.add_argument('-from', '--from-addr', dest='from_addr', type=str, default='')
    parser.add_argument('-to', '--to-addr', dest='to_addr', nargs='*', type=str, default='')
    parser.add_argument('-s', '--sources', dest='sources', nargs='?', help='Sources from json')
    parser.add_argument('-test', '--test-mode', dest='test_mode', action='store_true', default=False)
    args = parser.parse_args()

    user_name = args.username or input('Логин: ')
    user_pass = args.password or getpass('Пароль: ')


    with open(SCHEMA_MAPPING['get'], 'r') as f:
        if args.test_mode:
            sources = get_test_set(as_json=True)
        else:
            # sources = args.sources or ( sys.stdin.read().strip() or print('No data provided. Stopped.') or sys.exit(0) )
            sources = args.sources or ( input('Data waiting ...') or sys.exit(0) )

        schema = json.load(f)
        validator = Draft4Validator(schema)
        data = json.loads(sources)
        validator.validate(data)

        ### Задача асинхронного получения заголовков и тел писем
        task = create_task(start_async(
            data['data'],
            host=args.host,
            port=args.port,
            send_from=args.from_addr,
            send_to=args.to_addr,
            username=user_name,
            password=user_pass,
            report_width=args.report_width,
            report_height=args.report_height,
            executor=executor,
            loop=None
        ))

        await task





def main():
    with ProcessPoolExecutor(THREAD_WORKERS_COUNT) as executor:
        run_async(func(executor))





if __name__ == "__main__":
    main()
