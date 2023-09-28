import json
import traceback

import boto3

budgets = boto3.client("budgets")
sns = boto3.resource("sns")

ACCOUNT_ID = sns.get_caller_identity()["Account"]


def lambda_handler(event, context):
    try:
        response = budgets.describe_budgets(AccountId=ACCOUNT_ID, MaxResults=99)
        budget = next(
            filter(lambda b: b["BudgetName"] == event["budget_id"], response["Budgets"])
        )
        budget["BudgetLimit"]["Amount"] = str(event["budget"])
        response = budgets.update_budget(AccountId=ACCOUNT_ID, NewBudget=budget)
        return {
            "status": "Success",
            "description": "Budget updated.",
            "budget": str(budget),
        }

    except Exception as e:
        tb = traceback.format_exc()
        raise RuntimeError(
            json.dumps(
                {
                    "status": "Failed",
                    "description": f"Failed to update budget: {e}.",
                    "traceback": str(tb),
                    "input": event,
                }
            )
        )
