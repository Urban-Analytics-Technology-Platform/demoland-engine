import os
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

AZURE = os.getenv("WEBSITE_SITE_NAME") == "demoland-api"
if AZURE:
    print("Running on Azure")

app.add_middleware(
    CORSMiddleware,
    allow_methods=["POST"],
    allow_origins=(
        ["https://urban-analytics-technology-platform.github.io"]
        if AZURE
        else ["http://localhost:5173"]
    ),
)

@dataclass
class ScenarioRequest:
    """
    A dataclass is used here instead of Pydantic's BaseModel because BaseModel
    reserves attributes beginning with `model_` for internal use. See
    https://github.com/pydantic/pydantic/issues/4915
    """
    scenario_json: dict
    model_identifier: str = "tyne_and_wear"


@app.get("/")
async def root_GET():
    """
    Returns a simple message. Azure periodically sends a request to this
    endpoint to check that the API is running.
    """
    return {"message": "Hello world from demoland-api!"}


@app.post("/")
async def root_POST(
    body: ScenarioRequest,
):
    """
    Returns a JSON object with the predicted indicator values and signature
    types for each geometry.

    See the `docker_usage.ipynb` notebook for example Python usage.
    """
    # Set the environment variable before importing to avoid loading default
    # Tyne and Wear data every time this endpoint is called.
    os.environ["DEMOLAND"] = body.model_identifier
    import demoland_engine

    scenario = body.scenario_json
    demoland_engine.data.change_area(body.model_identifier)

    df = demoland_engine.get_empty()
    for oa_code, vals in scenario.items():
        df.loc[oa_code] = list(vals.values())

    pred = demoland_engine.get_indicators(df, random_seed=42)
    sig = demoland_engine.data.FILEVAULT["oa_key"].primary_type.copy()

    mapping = {
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
    sig = sig.map(mapping)
    changed = df.signature_type[df.signature_type.notna()]
    sig.loc[changed.index] = changed
    pred["signature_type"] = sig
    pred = pred.dropna(subset=["signature_type"])

    return pred.to_dict("index")
