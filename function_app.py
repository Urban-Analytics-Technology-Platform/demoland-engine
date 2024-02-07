"""
Azure Function app for demoland-engine.

To deploy manually, either follow the steps in the demoland-project book:
https://urban-analytics-technology-platform.github.io/demoland-project/book/developer_notes.html

or trigger the deploy_azure_functions GitHub Action:
https://github.com/Urban-Analytics-Technology-Platform/demoland-engine/actions/workflows/deploy_azure_functions.yaml
"""

import azure.functions as func
import json
import os
import logging

app = func.FunctionApp()


@app.function_name(name="DemoLandEngine")
@app.route(route="scenario", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        logging.info("Received request with body:")
        logging.info(req_body)

        scenario = req_body["scenario_json"]
        model_identifier = req_body["model_identifier"]
        os.environ["DEMOLAND"] = model_identifier
        from demoland_engine.api import scenario_calc
        pred_dict = scenario_calc(scenario, model_identifier)
        return func.HttpResponse(json.dumps(pred_dict))
    except Exception as e:
        logging.error(e)

        return func.HttpResponse(json.dumps({
            "result": "error",
            "message": str(e)
        }))
