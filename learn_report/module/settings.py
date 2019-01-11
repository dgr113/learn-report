# coding: utf-8
import os
from multiprocessing import cpu_count



BASEDIR = os.path.abspath(os.path.dirname(__file__))


SCHEMA_MAPPING = {
    'get': os.path.join(BASEDIR, '_get.json')
}


### Многопроцессорная обработка
THREAD_WORKERS_COUNT = cpu_count() - 1
