import pooch

CACHE = None

registry = {
    "accessibility": "b227092882663d1f4172b745891ef2e7aca37000acf0ce6d5a5a4e34822edda8",
    "air_quality_predictor": "d72f5b99f4f2cbec516c580616df83c9d4a3991688ae9d6d1c82e072eb56224c",
    "default_data": "58398d595366e622997d9aa95b1e59f0ed07724efd5b773ee87f14c2375d3896",
    "empty_lsoa": "92daec9169bd517c3a4cda33369f2dc6d920f757682614ccfc7f080059c7043d",
    "empty": "7f31dec98c6b8d6649091936e00d11a36fe5e5507e92be9d4f5712a640d35d98",
    "house_price_predictor": "102de21218e3f135e8e23d9a4271cb356a49f43d9e0f3b1e66affbfecc26946c",
    "iqr_form": "c84a006f899831b5228a8756b055b7214289efebf349e226a55f1ce113898bb3",
    "iqr_function": "beaab3385b16a9f48cb104bf28066df84f41655fbbca400b5f6a74816df6d0e0",
    "lsoa_baseline": "c52e8f701b44e10721d933c944e48396b327ce25a9e1bc7a73bebf904e003311",
    "median_form": "efdb305603d4fbb394d7e4973d6c0a0dc0cf79c6a7f5f12dd83c0220501b6dc4",
    "median_function": "b92278503d78ee4bb84d58e0b77ccb7164fda06a59eba8a559f7b22db65395ac",
    "oa_area": "52b4736efaad1b54ad939166a12d094938b4a4ffc48968ad056f4c50f5b837ba",
    "oa_key": "133ceefae188b19f35c0f03fbaffbe9b1d6642062e62818770bcf92baa72517b",
    "oa_lsoa": "0ee90cb1f63454b86ece57870029eef0002c457b29849e59485fe09672c5316e",
    "oa_order": "1e514a29ddbdc46016572f8ebcd5a58d76c3c46748472cd5a0d6dc24cd852bc4",
}


urls = {
    "accessibility": "accessibility.joblib",
    "air_quality_predictor": "air_quality_predictor_nc_urbanities.pickle",
    "default_data": "default_data.parquet",
    "empty_lsoa": "empty_lsoa.parquet",
    "empty": "empty.parquet",
    "house_price_predictor": "house_price_predictor_england_no_london.pickle",
    "iqr_form": "iqr_form.parquet",
    "iqr_function": "iqr_function.parquet",
    "lsoa_baseline": "lsoa_baseline.parquet",
    "median_form": "median_form.parquet",
    "median_function": "median_function.parquet",
    "oa_area": "oa_area.parquet",
    "oa_key": "oa_key.parquet",
    "oa_lsoa": "oa_lsoa.parquet",
    "oa_order": "oa_order.parquet",
}

try:
    import pyodide_js
    BASE_URL = pyodide_js.globals.get("BASE_URL") + "/data/"
    registry = {
        **registry,
        "air_quality_predictor": "4d425e53bf6a1cb53a0614225c4b5e5c78d993b6cf4d83a309921c212660a06c",
        "house_price_predictor": "1eb2c4ccad77149e2122cd6c42fc4c094b82c579af15186e6fdeca5504d414f6"
    }
    urls = {
        **urls,
        "house_price_predictor": "house_predictor_model_wasm.pickle",
        "air_quality_predictor": "air_predictor_model_wasm.pickle"
    }
except Exception as e:
    print(f"Encountered error: {e}. Defaulting to data on GitHub.")
    BASE_URL = "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/"

print("BASE_URL ", BASE_URL);
urls = {a :f"{BASE_URL}{b}" for (a, b) in urls.items() }

print("urls ", urls);
print("registry ", registry)

CACHE = pooch.create(
    path=pooch.os_cache("demoland_engine"),
    base_url="",
    registry=registry,
    urls=urls
)
