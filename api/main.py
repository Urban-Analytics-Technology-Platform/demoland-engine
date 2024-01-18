"""
FastAPI server, allowing for scenario calculation over HTTP.

To run, cd to the top level of the git repo (not the `api` directory) and run

    python -m pip install .[api]
    uvicorn main:app --app-dir api --port 5178

For more details, see
https://urban-analytics-technology-platform.github.io/demoland-project/book/developer_notes.html
"""

import os
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_methods=["POST"],
    allow_origins=["*"],
)

@dataclass
class ScenarioRequest:
    """
    A dataclass is used here instead of Pydantic's BaseModel because BaseModel
    reserves attributes beginning with `model_` for internal use. See
    https://github.com/pydantic/pydantic/issues/4915
    """
    scenario_json: dict
    model_identifier: str


@app.post("/api/scenario")
async def root_POST(
    body: ScenarioRequest,
):
    """
    Returns a JSON object with the predicted indicator values and signature
    types for each geometry.

    See the documentation of `scenario_calc`, or the 'Developer Notes' section
    of the DemoLand project book, for more details.

    https://urban-analytics-technology-platform.github.io/demoland-project/book/developer_notes.html
    """
    scenario = body.scenario_json
    model_identifier = body.model_identifier

    # Set the environment variable before importing to avoid loading default
    # Tyne and Wear data every time this endpoint is called
    os.environ["DEMOLAND"] = model_identifier
    from demoland_engine.api import scenario_calc
    return scenario_calc(scenario, model_identifier)
