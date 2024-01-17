import azure.functions as func
import json
import os
import logging

app = func.FunctionApp()

@app.function_name(name="DemoLandEngine")
@app.route(route="scenario", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Returns a JSON object with the predicted indicator values and signature
    types for each OA.

    See the `docker_usage.ipynb` notebook for example Python usage.
    """
    try:
        # Set the environment variable before importing to avoid loading
        # default Tyne and Wear data every time this endpoint is called.
        req_body = req.get_json()
        scenario = req_body["scenario_json"]
        os.environ["DEMOLAND"] = req_body["model_identifier"]
        import demoland_engine

        logging.info("Received request with body:")
        logging.info(req_body)

        # This is no longer needed because Azure functions don't have
        # persistent state (I _think_).
        # demoland_engine.data.change_area(body.model_identifier)

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

        return func.HttpResponse(json.dumps(pred.to_dict("index")))
    except Exception as e:
        return func.HttpResponse(json.dumps({
            "result": "error",
            "message": str(e)
        }))
