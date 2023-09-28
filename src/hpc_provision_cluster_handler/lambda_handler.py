import json
import os
import traceback

import urllib3

http = urllib3.PoolManager()
PCLUSTER_CONFIG = """
Image:
  Os: alinux2
HeadNode:
  InstanceType: {{ head_node_instance_type }}
  Networking:
    SubnetId: {{ head_node_subnet_id }}
    ElasticIp: true
  Ssh:
    KeyName: {{ ec2_key_pair_name }}
Scheduling:
  Scheduler: slurm
  SlurmQueues:
    - Name: queue
      Networking:
        SubnetIds:
          - {{ worker_node_subnet_id }}
      ComputeResources:
        - Name: compute-resource
          InstanceType: {{ worker_node_instance_type }}
          MinCount: {{ worker_node_min_count}}
          MaxCount: {{ worker_node_max_count}}
          SpotPrice: 1.1
          DisableSimultaneousMultithreading: true
Tags:
  - Key: requestor_email
    Value: {{ requestor_email }}
  - Key: requestor_division
    Value: {{ requestor_division }}
  - Key: purpose
    Value: {{ purpose }}
  - Key: admin_email
    Value: {{ admin_email }}
"""
API_KEY = os.environ.get("API_KEY")
API_ENDPOINT = os.environ.get("API_ENDPOINT")
BASE_URL = f"https://{API_ENDPOINT}/prod/v3/clusters"


def lambda_handler(event, context):
    try:
        body = {
            "clusterName": event["cluster_name"],
            "clusterConfiguration": PCLUSTER_CONFIG.format(**event),
            "region": "us-east-1",
        }
        encoded_body = json.dumps(body).encode("utf-8")
        r = http.request(
            method="POST",
            url=BASE_URL,
            body=encoded_body,
            headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
            timeout=urllib3.util.Timeout(120),
        )
        # TODO - Invoke CloudFormation build BudgetName = ClusterName, BudgetAmount
        return {"status": "Success", "response": r.data}
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
