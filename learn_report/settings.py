# coding: utf-8

import os
from multiprocessing import cpu_count



BASEDIR = os.path.abspath(os.path.dirname(__file__))


SCHEMA_MAPPING = {
    'get': os.path.join(BASEDIR, 'module', '_get.json')
}


FONTS_DIR = os.path.join(BASEDIR, 'sources', 'fonts')
DEFAULT_FONT_PATH = os.path.join(FONTS_DIR, 'FreeSans.ttf')


### Многопроцессорная обработка
THREAD_WORKERS_COUNT = cpu_count() - 1
