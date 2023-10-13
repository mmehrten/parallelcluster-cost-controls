import json
import os
import traceback

import urllib3

http = urllib3.PoolManager()

API_KEY = os.environ.get("API_KEY")
API_ENDPOINT = os.environ.get("API_ENDPOINT")
BASE_URL = f"{API_ENDPOINT}/v3/clusters"
REGION = os.environ["AWS_REGION"]


def lambda_handler(event, context):
    try:
        cluster_name = event["cluster_name"]
        body = {
            "status": "STOP_REQUESTED",
            "region": REGION,
        }

        encoded_body = json.dumps(body).encode("utf-8")
        r = http.request(
            method="PATCH",
            url=f"{BASE_URL}/{cluster_name}/computefleet",
            body=encoded_body,
            headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
            timeout=urllib3.util.Timeout(120),
        )
        if r.status > 299:
            raise RuntimeError(f"{r.status}: {r.data.decode('utf-8')}")
        return {"status": "Success", "response": r.data}
    except Exception as e:
        tb = traceback.format_exc()
        raise RuntimeError(
            json.dumps(
                {
                    "status": "Failed",
                    "description": f"Failed to pause cluster: {e}.",
                    "traceback": str(tb),
                    "input": event,
                }
            )
        )
