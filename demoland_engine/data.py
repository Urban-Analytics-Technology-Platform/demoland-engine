import os

import joblib
import numpy as np
import pandas as pd
import pooch
from .graph import read_parquet

study_area = os.environ.get("DEMOLAND", "tyne_and_wear")

files = {
    "tyne_and_wear": {
        "registry": {
            # globally shared files
            "median_form": "efdb305603d4fbb394d7e4973d6c0a0dc0cf79c6a7f5f12dd83c0220501b6dc4",
            "median_function": "b92278503d78ee4bb84d58e0b77ccb7164fda06a59eba8a559f7b22db65395ac",
            "iqr_form": "c84a006f899831b5228a8756b055b7214289efebf349e226a55f1ce113898bb3",
            "iqr_function": "beaab3385b16a9f48cb104bf28066df84f41655fbbca400b5f6a74816df6d0e0",
            # locally specific files
            "accessibility": "b227092882663d1f4172b745891ef2e7aca37000acf0ce6d5a5a4e34822edda8",
            "air_quality_predictor": "5303c046d3c177147577e8dfa4373f5c82f10d05a4d5b5b771cd2a1b73274393",
            "default_data": "58398d595366e622997d9aa95b1e59f0ed07724efd5b773ee87f14c2375d3896",
            "empty_lsoa": "92daec9169bd517c3a4cda33369f2dc6d920f757682614ccfc7f080059c7043d",
            "empty": "7f31dec98c6b8d6649091936e00d11a36fe5e5507e92be9d4f5712a640d35d98",
            "house_price_predictor": "843fd29c05fb28df199fb8d4048d4f2cf6584fa550c5a8ee27eced09494433bd",
            "lsoa_baseline": "c52e8f701b44e10721d933c944e48396b327ce25a9e1bc7a73bebf904e003311",
            "oa_area": "52b4736efaad1b54ad939166a12d094938b4a4ffc48968ad056f4c50f5b837ba",
            "oa_key": "133ceefae188b19f35c0f03fbaffbe9b1d6642062e62818770bcf92baa72517b",
            "oa_lsoa": "0ee90cb1f63454b86ece57870029eef0002c457b29849e59485fe09672c5316e",
            "oa_order": "1e514a29ddbdc46016572f8ebcd5a58d76c3c46748472cd5a0d6dc24cd852bc4",
            "matrix": "eb194edc8fca9a3ab5d92160cd98d6a680657fe469547b32281cfa13ffb8ba17",
            "air_quality_model": "4f95ca4033bc1723b369ce84b4dff0de75be2ed1b6556d6d12add773ba1f9b28",
            "house_price_model": "b6fa464ed88848b7829d15c1a904b5b754e31ed1e44bd2ab4a716e74a7d6ae72",
        },
        "urls": {
            # globally shared files
            "median_form": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/median_form.parquet",
            "median_function": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/median_function.parquet",
            "iqr_form": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/iqr_form.parquet",
            "iqr_function": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/iqr_function.parquet",
            # locally specific files
            "accessibility": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/accessibility.joblib",
            "air_quality_predictor": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/air_quality_predictor_nc_urbanities.pickle",
            "default_data": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/default_data.parquet",
            "empty_lsoa": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/empty_lsoa.parquet",
            "empty": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/empty.parquet",
            "house_price_predictor": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/house_price_predictor_england_no_london.pickle",
            "lsoa_baseline": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/lsoa_baseline.parquet",
            "oa_area": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/oa_area.parquet",
            "oa_key": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/oa_key.parquet",
            "oa_lsoa": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/oa_lsoa.parquet",
            "oa_order": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/oa_order.parquet",
            "matrix": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/matrix.parquet",
            "air_quality_model": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/air_quality_model.joblib",
            "house_price_model": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/house_price_model.joblib",
        },
    },
    "tyne_and_wear_hex": {
        "registry": {
            # globally shared files
            "air_quality_model": "42b8080172cdad413b9d3c9d322ef32979900b4f63bc61a45b543cd8c60d4a2d",
            "house_price_model": "eb9eebfac8ea417f6b4ded0e203be9144408d7241a55501896b5ead2edf25162",
            "median_form": "efdb305603d4fbb394d7e4973d6c0a0dc0cf79c6a7f5f12dd83c0220501b6dc4",
            "median_function": "b92278503d78ee4bb84d58e0b77ccb7164fda06a59eba8a559f7b22db65395ac",
            "iqr_form": "c84a006f899831b5228a8756b055b7214289efebf349e226a55f1ce113898bb3",
            "iqr_function": "beaab3385b16a9f48cb104bf28066df84f41655fbbca400b5f6a74816df6d0e0",
            # locally specific files
            "accessibility": "df3ca485fb9b57414453a5e0b137b4e11bab30e27d2091cd0bbd93334fd5c7b2",
            "matrix": "f4b643b9d233985cf25ca7ad47963e4c4274fe693e6f669fce9590e7048c9d7b",
            "default_data": "87d045553f07f5c1984cb575b85d1412018b24f899b2e959b611105a15789a1d",
            "empty": "45e1cdfe94997e9577775afcec9eddfbb28f70467be922be482308a95065d367",
            "oa_area": "2dc67bc52ce06485c8f6e0c0e621ecc15650d298292f985f68c00239c49da50a",
            "oa_key": "f84c46d2d6e77cfa29ab5128b80e6b401683b019440169a64085a56cbd725a82",
        },
        "urls": {
            # globally shared files
            "air_quality_model": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/air_quality_model.joblib",
            "house_price_model": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/house_price_model.joblib",
            "median_form": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/median_form.parquet",
            "median_function": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/median_function.parquet",
            "iqr_form": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/iqr_form.parquet",
            "iqr_function": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/global/iqr_function.parquet",
            # locally specific files
            "accessibility": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear_hex/accessibility.joblib",
            "matrix": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear_hex/matrix.parquet",
            "default_data": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear_hex/default_data.parquet",
            "empty": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear_hex/empty.parquet",
            "oa_area": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear_hex/oa_area.parquet",
            "oa_key": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear_hex/oa_key.parquet",
        },
    },
}


CACHE = pooch.create(
    path=pooch.os_cache("demoland_engine"),
    base_url="",
    registry=files[study_area]["registry"],
    urls=files[study_area]["urls"],
)

# The following code deals with an error in the sklearn code which makes pickles
# not protable between 64 and 32 bit environments.

Y_DTYPE = np.float64
X_DTYPE = np.float64
X_BINNED_DTYPE = np.uint8  # hence max_bins == 256
# dtype for gradients and hessians arrays
G_H_DTYPE = np.float32
X_BITSET_INNER_DTYPE = np.uint32

PREDICTOR_RECORD_DTYPE_2 = np.dtype(
    [
        ("value", Y_DTYPE),
        ("count", np.uint32),
        ("feature_idx", np.int32),
        ("num_threshold", X_DTYPE),
        ("missing_go_to_left", np.uint8),
        ("left", np.uint32),
        ("right", np.uint32),
        ("gain", Y_DTYPE),
        ("depth", np.uint32),
        ("is_leaf", np.uint8),
        ("bin_threshold", X_BINNED_DTYPE),
        ("is_categorical", np.uint8),
        # The index of the corresponding bitsets in the Predictor's bitset arrays.
        # Only used if is_categorical is True
        ("bitset_idx", np.uint32),
    ]
)


# pooch processor to fix pyodide bug
def pyodide_convertor(fname, action, pup):
    try:
        # Check to see if we are in a pyodide environment
        import pyodide_js

        model = joblib.load(fname)
        for i, _ in enumerate(model._predictors):
            model._predictors[i][0].nodes = model._predictors[i][0].nodes.astype(
                PREDICTOR_RECORD_DTYPE_2, casting="same_kind"
            )
        fname_base = fname.split(".")[0]
        new_fname = f"{fname_base}_pyodide.joblib"
        joblib.dump(new_fname, model)
        return new_fname
    except ImportError:
        return fname


FILEVAULT = dict(
    case=study_area,
    empty=pd.read_parquet(CACHE.fetch("empty")),
    matrix=read_parquet(CACHE.fetch("matrix")),
    median_form=pd.read_parquet(CACHE.fetch("median_form")),
    iqr_form=pd.read_parquet(CACHE.fetch("iqr_form")),
    median_function=pd.read_parquet(CACHE.fetch("median_function")),
    iqr_function=pd.read_parquet(CACHE.fetch("iqr_function")),
    oa_key=pd.read_parquet(CACHE.fetch("oa_key")),
    oa_area=pd.read_parquet(CACHE.fetch("oa_area")),
    default_data=pd.read_parquet(CACHE.fetch("default_data")),
)

with open(CACHE.fetch("air_quality_model", processor=pyodide_convertor), "rb") as f:
    FILEVAULT["aq_model"] = joblib.load(f)

with open(CACHE.fetch("house_price_model", processor=pyodide_convertor), "rb") as f:
    FILEVAULT["hp_model"] = joblib.load(f)

with open(CACHE.fetch("accessibility"), "rb") as f:
    FILEVAULT["accessibility"] = joblib.load(f)


def change_area(study_area):
    """Load the data for another study area

    Parameters
    ----------
    study_area : str
        name of the study area
    """
    # replace files within filevault with those representing a new area
    FILEVAULT["case"] = study_area

    CACHE = pooch.create(
        path=pooch.os_cache("demoland_engine"),
        base_url="",
        registry=files[study_area]["registry"],
        urls=files[study_area]["urls"],
    )
    FILEVAULT["empty"] = pd.read_parquet(CACHE.fetch("empty"))
    FILEVAULT["matrix"] = read_parquet(CACHE.fetch("matrix"))
    FILEVAULT["median_form"] = pd.read_parquet(CACHE.fetch("median_form"))
    FILEVAULT["iqr_form"] = pd.read_parquet(CACHE.fetch("iqr_form"))
    FILEVAULT["median_function"] = pd.read_parquet(CACHE.fetch("median_function"))
    FILEVAULT["iqr_function"] = pd.read_parquet(CACHE.fetch("iqr_function"))
    FILEVAULT["oa_key"] = pd.read_parquet(CACHE.fetch("oa_key"))
    FILEVAULT["oa_area"] = pd.read_parquet(CACHE.fetch("oa_area"))
    FILEVAULT["default_data"] = pd.read_parquet(CACHE.fetch("default_data"))

    with open(CACHE.fetch("air_quality_model"), "rb") as f:
        FILEVAULT["aq_model"] = joblib.load(f)

    with open(CACHE.fetch("house_price_model"), "rb") as f:
        FILEVAULT["hp_model"] = joblib.load(f)

    with open(CACHE.fetch("accessibility"), "rb") as f:
        FILEVAULT["accessibility"] = joblib.load(f)
