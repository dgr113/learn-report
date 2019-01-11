# coding: utf-8

import enum
import json
import numpy as np
import pandas as pd
from dataclasses import asdict
from datetime import datetime, date, time
from typing import Any
from learn_report.module.functions import get_axis_color_mask
from learn_report.module.data_structs import TableDesc



def _as_serializable(x: Any) -> Any:
    """ Подготовка значений для сериализации """

    if isinstance(x, TableDesc):
        result = asdict(x)
    elif isinstance(x, pd.DataFrame):
        # noinspection PyUnresolvedReferences
        result = x.astype(object).values.tolist()
    elif isinstance(x, np.ndarray):
        result = x.astype(object).tolist()
    elif isinstance(x, (datetime, date, time, pd.Timestamp)):
        result = x.isoformat()
    elif isinstance(x, enum.Enum):
        result = x.value
    else:
        result = None

    return result




def get_test_set(as_json: bool = False):
    """ Тестовый набор данных для отчета """

    X1 = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': [1, 2, 3, 4],
        'C': [1, 2, 3, 4],
    })
    y1 = np.array([1, 2, 2, 2])
    colors_mask1 = get_axis_color_mask(X1, y1, color_mapping={1: 'green', 2: 'red'})

    results = [
        # one report in reports array
        [
            TableDesc(X1, colors_mask1),  # one table in report
        ]
    ]

    if as_json:
        results = json.dumps({'data': results}, default=_as_serializable)

    return results
