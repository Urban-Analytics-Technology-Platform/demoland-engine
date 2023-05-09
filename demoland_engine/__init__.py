from .predictors import get_indicators, get_indicators_lsoa  # noqa
from .engine import Engine  # noqa
from .baselines import get_empty, get_empty_lsoa, get_lsoa_baseline  # noqa

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("demoland_engine")
except PackageNotFoundError:  # noqa
    # package is not installed
    pass
