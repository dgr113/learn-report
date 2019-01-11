# coding: utf-8

import numpy as np
import pandas as pd
from typing import Union, List


MAIL_ADDRESSES_TYPE = Union[str, List[str]]
TABLE_DATA_TYPE = pd.DataFrame
TABLE_MASK_TYPE = Union[pd.DataFrame, None]
STYLES_LIST_TYPE = List[list]
VECTORIZED_ARRAY_TYPE = Union[np.array, pd.Series]
