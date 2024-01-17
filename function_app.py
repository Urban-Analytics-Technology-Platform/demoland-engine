import azure.functions as func
import json
import os
import logging

app = func.FunctionApp()


def scenario_calc(scenario: dict, model_identifier: str):
    """
    Returns a JSON object with the predicted indicator values and signature
    types for each OA.

    See the `docker_usage.ipynb` notebook for example Python usage.
    """
    os.environ["DEMOLAND"] = model_identifier
    import demoland_engine
    demoland_engine.data.change_area(model_identifier)

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


@app.function_name(name="DemoLandEngine")
@app.route(route="scenario", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        logging.info("Received request with body:")
        logging.info(req_body)

        result = scenario_calc(req_body["scenario_json"], req_body["model_identifier"])
        return func.HttpResponse(json.dumps(result))
    except Exception as e:
        logging.error(e)

        return func.HttpResponse(json.dumps({
            "result": "error",
            "message": str(e)
        }))
