# coding: utf-8

from dataclasses import make_dataclass
from learn_report.module.type_hints import TABLE_DATA_TYPE, TABLE_MASK_TYPE




TableDesc = make_dataclass(
    'TableDesc',
    [
        ('data', TABLE_DATA_TYPE),
        ('mask', TABLE_MASK_TYPE)
    ],
    frozen=True
)
