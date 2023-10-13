import json
import os
import time
import traceback

import botocore.session
import urllib3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

http = urllib3.PoolManager()
PCLUSTER_CONFIG = """
Image:
  Os: alinux2
HeadNode:
  InstanceType: {head_node_instance_type}
  Networking:
    SubnetId: {head_node_subnet_id}
    ElasticIp: true
  Ssh:
    KeyName: {ec2_key_pair_name}
Scheduling:
  Scheduler: slurm
  SlurmQueues:
    - Name: queue
      Networking:
        SubnetIds:
          - {worker_node_subnet_id}
      ComputeResources:
        - Name: compute-resource
          InstanceType: {worker_node_instance_type}
          MinCount: {worker_node_min_count}
          MaxCount: {worker_node_max_count}
          SpotPrice: 1.1
          DisableSimultaneousMultithreading: true
Tags:
  - Key: requestor_email
    Value: {requestor_email}
  - Key: requestor_division
    Value: {requestor_division}
  - Key: purpose
    Value: {purpose}
  - Key: admin_email
    Value: {admin_email}
"""
API_KEY = os.environ.get("API_KEY")
API_ENDPOINT = os.environ.get("API_ENDPOINT")
BASE_URL = f"{API_ENDPOINT}/v3/clusters"
REGION = os.environ["AWS_REGION"]


def _request(url, method, body, headers):
    encoded_body = json.dumps(body)
    session = botocore.session.Session()
    sigv4 = SigV4Auth(session.get_credentials(), "execute-api", REGION)
    request = AWSRequest(
        method=method,
        url=url,
        data=encoded_body,
        headers=headers,
    )
    request.context["payload_signing_enabled"] = True
    sigv4.add_auth(request)
    prepped = request.prepare()

    r = http.request(
        method=method,
        url=prepped.url,
        body=encoded_body,
        headers=prepped.headers,
        timeout=urllib3.util.Timeout(120),
    )
    print(
        json.dumps(
            {
                "event": "http_request",
                "response_code": r.status,
                "response": r.data.decode("utf-8"),
            }
        )
    )
    if r.status > 299:
        raise RuntimeError(f"{r.status}: {r.data.decode('utf-8')}")
    return r


def lambda_handler(event, context):
    try:
        body = {
            "clusterName": event["cluster_name"],
            "clusterConfiguration": PCLUSTER_CONFIG.format(**event),
            "region": "us-east-1",
        }
        r = _request(
            url=BASE_URL,
            method="POST",
            body=body,
            headers={"Content-Type": "application/json"},
        )
        data = json.loads(r.data)
        # Wait up to a minute for the cluster to finish creating - progressing >30 seconds in the
        # deployment will generally mean we don't have any configuration errors
        slept = 0
        while (
            r.status != 200
            or data["cloudFormationStackStatus"]
            not in (
                "CREATE_COMPLETE",
                "FAILED",
                "ROLLBACK_COMPLETE",
                "ROLLBACK_IN_PROGRESS",
            )
        ) and slept < 60:
            r = _request(
                url=f"{BASE_URL}/{event['cluster_name']}",
                method="GET",
                body=body,
                headers={"Content-Type": "application/json"},
            )
            data = json.loads(r.data)
            time.sleep(3)
            slept += 3
        # TODO - Invoke CloudFormation build BudgetName = ClusterName, BudgetAmount
        return {"status": "Success", "response": json.loads(r.data)}
    except Exception as e:
        tb = traceback.format_exc()
        raise RuntimeError(
            json.dumps(
                {
                    "status": "Failed",
                    "description": f"Failed to provision cluster: {e}.",
                    "traceback": str(tb),
                    "input": event,
                }
            )
        )
