from importlib.resources import files
import pandas as pd

root = files("demoland_engine.data")


def get_empty():
    return pd.read_parquet(root.joinpath("empty.parquet"))


def get_empty_lsoa():
    return pd.read_parquet(root.joinpath("empty_lsoa.parquet"))


def get_lsoa_baseline():
    return pd.read_parquet(root.joinpath("lsoa_baseline.parquet"))
