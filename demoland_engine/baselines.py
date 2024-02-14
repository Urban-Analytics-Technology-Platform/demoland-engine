import pandas as pd

from .data import CACHE, FILEVAULT, fetch_with_headers


def get_empty():
    return FILEVAULT["empty"]


def get_empty_lsoa():
    return pd.read_parquet(fetch_with_headers(CACHE, "empty_lsoa.parquet"))


def get_lsoa_baseline():
    return pd.read_parquet(fetch_with_headers(CACHE, "lsoa_baseline.parquet"))
