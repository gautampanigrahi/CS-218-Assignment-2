import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    employee_id = event["pathParameters"]["id"]

    result = table.get_item(
        Key={
            "EmployeeID": employee_id
        }
    )

    item = result.get("Item")

    if not item:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Employee not found"
            })
        }

    employee = {
        "employeeId": item["EmployeeID"],
        "name": item["Name"],
        "salary": int(item["Salary"]),
        "dateOfJoin": item["DateOfJoin"],
        "description": item["Description"]
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(employee)
    }
