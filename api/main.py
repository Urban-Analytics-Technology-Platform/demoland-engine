import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import demoland_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://alan-turing-institute.github.io"],
    allow_methods=["POST"],
)

class ScenarioJSON(BaseModel):
    scenario_json: dict


@app.post("/")
async def root(
    scenario_json: ScenarioJSON,
):
    scenario = scenario_json.scenario_json
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
