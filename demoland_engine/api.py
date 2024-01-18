from . import data
from .baselines import get_empty
from .predictors import get_indicators


SIG_MAPPING = {
    "Wild countryside": 0,
    "Countryside agriculture": 1,
    "Urban buffer": 2,
    "Warehouse/Park land": 3,
    "Open sprawl": 4,
    "Disconnected suburbia": 5,
    "Accessible suburbia": 6,
    "Connected residential neighbourhoods": 7,
    "Dense residential neighbourhoods": 8,
    "Gridded residential quarters": 9,
    "Dense urban neighbourhoods": 10,
    "Local urbanity": 11,
    "Regional urbanity": 12,
    "Metropolitan urbanity": 13,
    "Concentrated urbanity": 14,
    "Hyper concentrated urbanity": 15,
}


def scenario_calc(scenario: dict, model_identifier: str) -> dict:
    """
    Parameters
    ----------
    scenario : dict[str, dict[str, float]]
        A dictionary mapping area identifiers (strings) to the values of the
        input variables. The keys of the inner dictionary are 'signature_type',
        'job', 'use', and 'greenspace'.

    model_identifier : str
        The name of the model to use. See the `data` top-level directory for
        available names.

    Returns
    -------
    pred : dict[str, dict[str, float]]
        Spatial signatures and predicted indicator values for each area
        identifier. The spatial signatures are the same as those given in the
        input scenario, but are included here for ease of use downstream. The
        keys of the inner dictionary are 'signature_type', 'house_price',
        'air_quality', 'job_accessibility', and 'greenspace_accessibility'.

    This function is used both by the FastAPI app (api/main.py) and the Azure
    Functions app (function_app.py).
    """
    data.change_area(model_identifier)

    df = get_empty()
    for oa_code, vals in scenario.items():
        df.loc[oa_code] = list(vals.values())

    pred = get_indicators(df, random_seed=42)
    sig = data.FILEVAULT["oa_key"].primary_type.copy()

    sig = sig.map(SIG_MAPPING)
    changed = df.signature_type[df.signature_type.notna()]
    sig.loc[changed.index] = changed
    pred["signature_type"] = sig
    pred = pred.dropna(subset=["signature_type"])

    return pred.to_dict("index")
