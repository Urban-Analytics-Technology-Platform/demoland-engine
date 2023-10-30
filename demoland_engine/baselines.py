import pandas as pd

from .data import CACHE


def get_empty():
    return pd.read_parquet(CACHE.fetch("empty"))


def get_empty_lsoa():
    return pd.read_parquet(CACHE.fetch("empty_lsoa.parquet"))


def get_lsoa_baseline():
    return pd.read_parquet(CACHE.fetch("lsoa_baseline.parquet"))
