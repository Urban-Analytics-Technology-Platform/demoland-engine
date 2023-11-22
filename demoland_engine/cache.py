import pooch
import aiohttp

from pathlib import Path
import hashlib
from collections import namedtuple
import asyncio

CacheTarget = namedtuple("CacheTarget", ["key", "url", "sha256"])

class AsyncCache():
    def __init__(self, files: list[CacheTarget], base_url="", path = None):
        if path is None:
            self.path = Path(pooch.os_cache("demoland_engine"))
        else:
            self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.files = files
        self.base_url = base_url
        asyncio.run(self.download_all_async())

    async def download_all_async(self):
        """Download all files asynchronously."""
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[self.download_async(file, session) for file in self.files]
            )

    async def download_async(self, file: CacheTarget, session: aiohttp.ClientSession):
        """Asynchronously stream a file download."""
        hasher = hashlib.sha256()
        async with session.get(self.base_url + "/" + file.url) as response:
            with open(self.path / file.key, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    f.write(chunk)
                    hasher.update(chunk)
        # Check SHA256 matches
        sha256 = hasher.hexdigest()
        if sha256 != file.sha256:
            raise ValueError(f"SHA256 mismatch for {file.key}: expected {file.sha256}, got {sha256}")

    def fetch(self, key):
        return str(self.path / key)

files = [
    CacheTarget(key="accessibility",
                url="accessibility.joblib",
                sha256="b227092882663d1f4172b745891ef2e7aca37000acf0ce6d5a5a4e34822edda8"),
    CacheTarget(key="default_data",
                url="default_data.parquet",
                sha256="58398d595366e622997d9aa95b1e59f0ed07724efd5b773ee87f14c2375d3896"),
    CacheTarget(key="empty_lsoa",
                url="empty_lsoa.parquet",
                sha256="92daec9169bd517c3a4cda33369f2dc6d920f757682614ccfc7f080059c7043d"),
    CacheTarget(key="empty",
                url="empty.parquet",
                sha256="7f31dec98c6b8d6649091936e00d11a36fe5e5507e92be9d4f5712a640d35d98"),
    CacheTarget(key="iqr_form",
                url="iqr_form.parquet",
                sha256="c84a006f899831b5228a8756b055b7214289efebf349e226a55f1ce113898bb3"),
    CacheTarget(key="iqr_function",
                url="iqr_function.parquet",
                sha256="beaab3385b16a9f48cb104bf28066df84f41655fbbca400b5f6a74816df6d0e0"),
    CacheTarget(key="lsoa_baseline",
                url="lsoa_baseline.parquet",
                sha256="c52e8f701b44e10721d933c944e48396b327ce25a9e1bc7a73bebf904e003311"),
    CacheTarget(key="median_form",
                url="median_form.parquet",
                sha256="efdb305603d4fbb394d7e4973d6c0a0dc0cf79c6a7f5f12dd83c0220501b6dc4"),
    CacheTarget(key="median_function",
                url="median_function.parquet",
                sha256="b92278503d78ee4bb84d58e0b77ccb7164fda06a59eba8a559f7b22db65395ac"),
    CacheTarget(key="oa_area",
                url="oa_area.parquet",
                sha256="52b4736efaad1b54ad939166a12d094938b4a4ffc48968ad056f4c50f5b837ba"),
    CacheTarget(key="oa_key",
                url="oa_key.parquet",
                sha256="133ceefae188b19f35c0f03fbaffbe9b1d6642062e62818770bcf92baa72517b"),
    CacheTarget(key="oa_lsoa",
                url="oa_lsoa.parquet",
                sha256="0ee90cb1f63454b86ece57870029eef0002c457b29849e59485fe09672c5316e"),
    CacheTarget(key="oa_order",
                url="oa_order.parquet",
                sha256="1e514a29ddbdc46016572f8ebcd5a58d76c3c46748472cd5a0d6dc24cd852bc4"),
]

try:
    import pyodide_js
    BASE_URL = pyodide_js.globals.get("BASE_URL") + "/data/"
    extra_files = [
        CacheTarget(key="air_quality_predictor",
                    url="air_predictor_model_wasm.pickle",
                    sha256="4d425e53bf6a1cb53a0614225c4b5e5c78d993b6cf4d83a309921c212660a06c"),
        CacheTarget(key="house_price_predictor",
                    url="house_predictor_model_wasm.pickle",
                    sha256="1eb2c4ccad77149e2122cd6c42fc4c094b82c579af15186e6fdeca5504d414f6")
    ]
except Exception as e:
    print(f"Encountered error loading Pyodide: {e}. Defaulting to data on GitHub.")
    BASE_URL = "https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/raw/main/data/tyne_and_wear/"
    extra_files = [
        CacheTarget(key="air_quality_predictor",
                    url="air_quality_predictor_nc_urbanities.pickle",
                    sha256="5303c046d3c177147577e8dfa4373f5c82f10d05a4d5b5b771cd2a1b73274393"),
        CacheTarget(key="house_price_predictor",
                    url="house_price_predictor_england_no_london.pickle",
                    sha256="843fd29c05fb28df199fb8d4048d4f2cf6584fa550c5a8ee27eced09494433bd"),
    ]

print("Using BASE_URL of: ", BASE_URL);

CACHE = AsyncCache(
    base_url=BASE_URL,
    files=files + extra_files
)
