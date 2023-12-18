import pooch
import numpy as np

registry = {
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
}
urls = {
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
}

CACHE = pooch.create(
    path=pooch.os_cache("demoland_engine"), base_url="", registry=registry, urls=urls
)

# The following code deals with an error in the sklearn code which makes pickles 
# not protable between 64 and 32 bit environments.

Y_DTYPE = np.float64
X_DTYPE = np.float64
X_BINNED_DTYPE = np.uint8  # hence max_bins == 256
# dtype for gradients and hessians arrays
G_H_DTYPE = np.float32
X_BITSET_INNER_DTYPE = np.uint32

PREDICTOR_RECORD_DTYPE_2 = np.dtype([
  ('value', Y_DTYPE),
  ('count', np.uint32),
  ('feature_idx', np.int32),
  ('num_threshold', X_DTYPE),
  ('missing_go_to_left', np.uint8),
  ('left', np.uint32),
  ('right', np.uint32),
  ('gain', Y_DTYPE),
  ('depth', np.uint32),
  ('is_leaf', np.uint8),
  ('bin_threshold', X_BINNED_DTYPE),
  ('is_categorical', np.uint8),
  # The index of the corresponding bitsets in the Predictor's bitset arrays.
  # Only used if is_categorical is True
  ('bitset_idx', np.uint32)
])

# pooch processor to fix pyodide bug
def pyodide_convertor(fname, action, pup):
    try:
        # Check to see if we are in a pyodide environment
        import pyodide_js
        model = joblib.load(fname)
        model._predictors[i][0].nodes = model._predictors[i][0].nodes.astype(PREDICTOR_RECORD_DTYPE_2, casting="same_kind")
        fname_base = fname.split(".")[0]
        new_fname = f"{fname_base}_pyodide.joblib"
        joblib.dump(new_fname, model)
        return new_fname
    except:
        return fname    
 
