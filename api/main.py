import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import demoland_engine

app = FastAPI()

AZURE = os.getenv("WEBSITE_SITE_NAME") == "demoland-api"
if AZURE:
    print("Running on Azure")

app.add_middleware(
    CORSMiddleware,
    allow_methods=["POST"],
    allow_origins=(["https://alan-turing-institute.github.io"]
                   if AZURE else ["http://localhost:5173"]),
)

class ScenarioJSON(BaseModel):
    scenario_json: dict

@app.get("/")
async def root_GET():
    """
    Returns a simple message. Azure periodically sends a request to this
    endpoint to check that the API is running.
    """
    return {"message": "Hello world from demoland-api!"}

@app.post("/")
async def root_POST(
    scenario_json: ScenarioJSON,
):
    """
    Returns a JSON object with the predicted indicator values and signature
    types for each OA.

    See the `docker_usage.ipynb` notebook for example Python usage.
    """
    scenario = scenario_json.scenario_json
    print(scenario)
    df = demoland_engine.get_empty()
    for oa_code, vals in scenario.items():
        df.loc[oa_code] = list(vals.values())

    pred = demoland_engine.get_indicators(df, random_seed=42)
    sig = demoland_engine.sampling.oa_key.primary_type.copy()

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

    return pred.to_dict("index")
