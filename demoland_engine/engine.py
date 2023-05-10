import pickle
from importlib.resources import files
import joblib
import pandas as pd

from .sampling import get_data, get_signature_values

root = files("demoland_engine.data")

lsoa_oa = pd.read_parquet(root.joinpath("oa_lsoa.parquet"))
lsoa_input = pd.read_parquet(root.joinpath("empty_lsoa.parquet"))
empty = pd.read_parquet(root.joinpath("empty.parquet"))


class Engine:
    def __init__(self, initial_state, random_seed=None) -> None:
        """Initialise the class and get the baseline indicators

        Parameters
        ----------
        initial_state : pandas.DataFrame
            DataFrame with specification of the initial state.
        """
        with open(
            root.joinpath("air_quality_predictor_nc_urbanities.pickle"), "rb"
        ) as f:
            self.air_quality_predictor = pickle.load(f)

        with open(
            root.joinpath("house_price_predictor_england_no_london.pickle"), "rb"
        ) as f:
            self.house_price_predictor = pickle.load(f)

        with open(root.joinpath("accessibility.joblib"), "rb") as f:
            self.accessibility = joblib.load(f)

        self.variable_state = (
            empty.assign(lsoa=lsoa_oa.lsoa11cd)[["lsoa"]]
            .merge(initial_state, left_on="lsoa", right_index=True, how="left")
            .drop(columns="lsoa")
        )
        self.random_seed = random_seed

        self.vars, self.jobs, self.gsp = get_data(
            self.variable_state, random_seed=self.random_seed
        )

        self.predict()

    def change(self, iloc, val):
        """Change a single variable on a single area and recompute indicators

        Parameters
        ----------
        iloc : tuple (row, col)
            tuple reflecitng the position of a change suitable for positional indexing
        val : float
            new value of a specified position
        """
        lsoa_key = lsoa_input.index[iloc[0]]
        affected_oa = lsoa_oa[lsoa_oa["lsoa11cd"] == lsoa_key].index
        changed_var = lsoa_input.columns[iloc[1]]
        self.variable_state.loc[affected_oa, changed_var] = val

        exvars = []
        jobs_diff = []
        gs_diff = []
        for vals in self.variable_state.loc[affected_oa].itertuples(name=None):
            ex, j, gs = get_signature_values(*vals, random_seed=self.random_seed)
            exvars.append(ex)
            jobs_diff.append(j)
            gs_diff.append(gs)

        self.vars.loc[affected_oa] = exvars
        self.jobs[affected_oa] = jobs_diff
        self.gsp[affected_oa] = gs_diff

        self.predict()

    def predict(self):
        aq = self.air_quality_predictor.predict(
            self.vars.rename(columns={"population_estimate": "population"})
        )
        hp = self.house_price_predictor.predict(
            self.vars.rename(columns={"population_estimate": "population"})
        )
        ja = self.accessibility.job_accessibility(self.jobs, "walk")
        gs = self.accessibility.greenspace_accessibility(self.gsp, "walk")
        ja = ja.to_pandas()[self.variable_state.index].values
        gs = gs.to_pandas()[self.variable_state.index].values

        self.indicators = (
            pd.DataFrame(
                {
                    "air_quality": aq,
                    "house_price": hp,
                    "job_accessibility": ja,
                    "greenspace_accessibility": gs,
                },
                index=self.variable_state.index,
            )
            .assign(lsoa=lsoa_oa.lsoa11cd)
            .groupby("lsoa")
            .mean()
        )
