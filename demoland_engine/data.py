import os

import pooch
import pandas as pd
import joblib
from libpysal import graph

study_area = os.environ.get("DEMOLAND", "tyne_and_wear")

files = {
    "tyne_and_wear": {
        "registry": {
            "accessibility": "b227092882663d1f4172b745891ef2e7aca37000acf0ce6d5a5a4e34822edda8",
            "air_quality_predictor": "5303c046d3c177147577e8dfa4373f5c82f10d05a4d5b5b771cd2a1b73274393",
            "default_data": "58398d595366e622997d9aa95b1e59f0ed07724efd5b773ee87f14c2375d3896",
            "empty_lsoa": "92daec9169bd517c3a4cda33369f2dc6d920f757682614ccfc7f080059c7043d",
            "empty": "7f31dec98c6b8d6649091936e00d11a36fe5e5507e92be9d4f5712a640d35d98",
            "house_price_predictor": "843fd29c05fb28df199fb8d4048d4f2cf6584fa550c5a8ee27eced09494433bd",
            "iqr_form": "c84a006f899831b5228a8756b055b7214289efebf349e226a55f1ce113898bb3",
            "iqr_function": "beaab3385b16a9f48cb104bf28066df84f41655fbbca400b5f6a74816df6d0e0",
            "lsoa_baseline": "c52e8f701b44e10721d933c944e48396b327ce25a9e1bc7a73bebf904e003311",
            "median_form": "efdb305603d4fbb394d7e4973d6c0a0dc0cf79c6a7f5f12dd83c0220501b6dc4",
            "median_function": "b92278503d78ee4bb84d58e0b77ccb7164fda06a59eba8a559f7b22db65395ac",
            "oa_area": "52b4736efaad1b54ad939166a12d094938b4a4ffc48968ad056f4c50f5b837ba",
            "oa_key": "133ceefae188b19f35c0f03fbaffbe9b1d6642062e62818770bcf92baa72517b",
            "oa_lsoa": "0ee90cb1f63454b86ece57870029eef0002c457b29849e59485fe09672c5316e",
            "oa_order": "1e514a29ddbdc46016572f8ebcd5a58d76c3c46748472cd5a0d6dc24cd852bc4",
            "matrix": "eb194edc8fca9a3ab5d92160cd98d6a680657fe469547b32281cfa13ffb8ba17",
            "air_quality_model": "1111815f4eacbedc12c3d221a34edf6147649bd5a8f9630e1f8a32b2494555b2",
            "house_price_model": "1c030fdfa4ddb8a7e08a6a0d55b0275f56a5986ea2bc6eb2d5367e12a6d79dc5",
        },
        "urls": {
            "accessibility": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/accessibility.joblib",
            "air_quality_predictor": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/air_quality_predictor_nc_urbanities.pickle",
            "default_data": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/default_data.parquet",
            "empty_lsoa": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/empty_lsoa.parquet",
            "empty": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/empty.parquet",
            "house_price_predictor": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/house_price_predictor_england_no_london.pickle",
            "iqr_form": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/iqr_form.parquet",
            "iqr_function": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/iqr_function.parquet",
            "lsoa_baseline": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/lsoa_baseline.parquet",
            "median_form": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/median_form.parquet",
            "median_function": "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/median_function.parquet",
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
            "air_quality_model": "a7e2ce3f995e6e76a85067ea2629f331e30f726242660a00ef6928d7e1fdb9d7",
            "house_price_model": "73411b560f0ad4eb8f15c51b748f8506ebbe487c9e787a6e925bcdca5ed7d12b",
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

FILEVAULT = dict(
    case=study_area,
    empty=pd.read_parquet(CACHE.fetch("empty")),
    matrix=graph.read_parquet(CACHE.fetch("matrix")),
    median_form=pd.read_parquet(CACHE.fetch("median_form")),
    iqr_form=pd.read_parquet(CACHE.fetch("iqr_form")),
    median_function=pd.read_parquet(CACHE.fetch("median_function")),
    iqr_function=pd.read_parquet(CACHE.fetch("iqr_function")),
    oa_key=pd.read_parquet(CACHE.fetch("oa_key")),
    oa_area=pd.read_parquet(CACHE.fetch("oa_area")),
    default_data=pd.read_parquet(CACHE.fetch("default_data")),
)

with open(CACHE.fetch("air_quality_model"), "rb") as f:
    FILEVAULT["aq_model"] = joblib.load(f)

with open(CACHE.fetch("house_price_model"), "rb") as f:
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
    FILEVAULT["matrix"] = graph.read_parquet(CACHE.fetch("matrix"))
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
