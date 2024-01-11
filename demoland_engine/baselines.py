import pandas as pd

from .data import CACHE, FILEVAULT


def get_empty():
    return FILEVAULT["empty"]


def get_empty_lsoa():
    return pd.read_parquet(CACHE.fetch("empty_lsoa.parquet"))


def get_lsoa_baseline():
    return pd.read_parquet(CACHE.fetch("lsoa_baseline.parquet"))
