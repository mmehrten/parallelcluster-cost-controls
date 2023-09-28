import json
import os
import traceback

import urllib3

http = urllib3.PoolManager()

API_KEY = os.environ.get("API_KEY")
API_ENDPOINT = os.environ.get("API_ENDPOINT")
BASE_URL = f"https://{API_ENDPOINT}/prod/v3/clusters"
REGION = os.environ['AWS_REGION']


def lambda_handler(event, context):
    try:
        cluster_name = event["cluster_name"]
        body = {"region": REGION}
        encoded_body = json.dumps(body).encode("utf-8")
        r = http.request(
            method="DELETE",
            url=f"{BASE_URL}/{cluster_name}",
            body=encoded_body,
            headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
            timeout=urllib3.util.Timeout(120),
        )
        return {"status": "Success", "response": r.data}
    except Exception as e:
        tb = traceback.format_exc()
        raise RuntimeError(
            json.dumps(
                {
                    "status": "Failed",
                    "description": f"Failed to delete cluster: {e}.",
                    "traceback": str(tb),
                    "input": event,
                }
            )
        )
