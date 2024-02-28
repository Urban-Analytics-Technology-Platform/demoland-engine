"""
Vendored from libpysal

Licedensed under the 3-Clause BSD License, Copyright (c) PySAL Developers

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

* Neither the name of the GeoDa Center for Geospatial Analysis and Computation
  nor the names of its contributors may be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

"""

from functools import cached_property
import pandas as pd
from scipy import sparse

ALLOWED_TRANSFORMATIONS = ("O", "B", "R", "D", "V", "C")

# listed alphabetically
__author__ = """"
Martin Fleischmann (martin@martinfleischmann.net)
Eli Knaap (ek@knaaptime.com)
Serge Rey (sjsrey@gmail.com)
Levi John Wolf (levi.john.wolf@gmail.com)
"""


class Graph:
    """Graph class encoding spatial weights matrices

    The :class:`Graph` is currently experimental
    and its API is incomplete and unstable.
    """

    def __init__(self, adjacency, transformation="O", is_sorted=False):
        """Weights base class based on adjacency list

        It is recommenced to use one of the ``from_*`` or ``build_*`` constructors
        rather than invoking ``__init__`` directly.

        Each observation needs to be present in the focal,
        at least as a self-loop with a weight 0.

        Parameters
        ----------
        adjacency : pandas.Series
            A MultiIndexed pandas.Series with ``"focal"`` and ``"neigbor"`` levels
            encoding adjacency, and values encoding weights. By convention,
            isolates are encoded as self-loops with a weight 0.
        transformation : str, default "O"
            weights transformation used to produce the table.

            - **O** -- Original
            - **B** -- Binary
            - **R** -- Row-standardization (global sum :math:`=n`)
            - **D** -- Double-standardization (global sum :math:`=1`)
            - **V** -- Variance stabilizing
            - **C** -- Custom
        is_sorted : bool, default False
            ``adjacency`` capturing the graph needs to be canonically sorted to
            initialize the class. The MultiIndex needs to be ordered i-->j
            on both focal and neighbor levels according to the order of ids in the
            original data from which the Graph is created. Sorting is performed by
            default based on the order of unique values in the focal level. Set
            ``is_sorted=True`` to skip this step if the adjacency is already canonically
            sorted.

        """
        if not isinstance(adjacency, pd.Series):
            raise TypeError(
                f"The adjacency table needs to be a pandas.Series. {type(adjacency)}"
            )
        if not adjacency.index.names == ["focal", "neighbor"]:
            raise ValueError(
                "The index of the adjacency table needs to be a MultiIndex named "
                "['focal', 'neighbor']."
            )
        if not adjacency.name == "weight":
            raise ValueError(
                "The adjacency needs to be named 'weight'. "
                f"'{adjacency.name}' was given instead."
            )
        if not pd.api.types.is_numeric_dtype(adjacency):
            raise ValueError(
                "The 'weight' needs to be of a numeric dtype. "
                f"'{adjacency.dtype}' dtype was given instead."
            )
        if adjacency.isna().any():
            raise ValueError("The adjacency table cannot contain missing values.")
        if transformation.upper() not in ALLOWED_TRANSFORMATIONS:
            raise ValueError(
                f"'transformation' needs to be one of {ALLOWED_TRANSFORMATIONS}. "
                f"'{transformation}' was given instead."
            )

        if not is_sorted:
            # adjacency always ordered i-->j on both levels
            ids = adjacency.index.get_level_values(0).unique().values
            adjacency = adjacency.reindex(ids, level=0).reindex(ids, level=1)

        self._adjacency = adjacency
        self.transformation = transformation

    @cached_property
    def sparse(self):
        """Return a scipy.sparse array (COO)

        Returns
        -------
        scipy.sparse.COO
            sparse representation of the adjacency
        """
        # pivot to COO sparse matrix and cast to array
        return sparse.coo_array(
            self._adjacency.astype("Sparse[float]").sparse.to_coo(sort_labels=True)[0]
        )

    def lag(self, y):
        """Spatial lag operator

        If weights are row standardized, returns the mean of each
        observation's neighbors; if not, returns the weighted sum
        of each observation's neighbors.

        Parameters
        ----------
        y : array-like
            array-like (N,) shape where N is equal to number of observations in self.

        Returns
        -------
        numpy.ndarray
            array of numeric values for the spatial lag
        """
        return self.sparse @ y


def read_parquet(path, **kwargs):
    """Read Graph from a Apache Parquet

    Read Graph serialized using `Graph.to_parquet()` back into the `Graph` object.
    The Parquet file needs to contain adjacency table with a structure required
    by the `Graph` constructor and optional metadata with the type of transformation.

    Parameters
    ----------
    path : str | pyarrow.NativeFile | file-like object
        path or any stream supported by pyarrow
    **kwargs
        additional keyword arguments passed to pyarrow.parquet.read_table

    Returns
    -------
    Graph
        deserialized Graph
    """
    adjacency, transformation = _read_parquet(path, **kwargs)
    return Graph(adjacency, transformation, is_sorted=False)


def _read_parquet(source, **kwargs):
    """Read libpysal-saved Graph object from Parquet

    Parameters
    ----------
    source : str | pyarrow.NativeFile
        path or any stream supported by pyarrow
    **kwargs
        additional keyword arguments passed to pyarrow.parquet.read_table

    Returns
    -------
    tuple
        tuple of adjacency table and transformation
    """
    return pd.read_parquet(source)["weight"], "R"
