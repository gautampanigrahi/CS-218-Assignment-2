# Assignment-2

## Overview

This project is a serverless HR application that allows an authenticated user to search for employee information using an Employee ID.

## AWS Services

- Amazon API Gateway REST API
- AWS Lambda
- Amazon DynamoDB
- Amazon Cognito
- AWS IAM

## Architecture

The browser sends requests to API Gateway. `GET /` invokes the UI Lambda and returns the application page. `GET /employee/{id}` is protected by a Cognito authorizer and invokes the backend Lambda. The backend Lambda reads the employee record from DynamoDB using the `EmployeeID` partition key.

The browser does not access DynamoDB directly.

## API Endpoints

```text
GET /
GET /employee/{id}
```

The employee endpoint requires a Cognito ID token in the `Authorization` header:

```text
Authorization: Bearer <Cognito ID token>
```

## DynamoDB

Table: `Employees`

Partition key: `EmployeeID`

Each record contains `EmployeeID`, `Name`, `Salary`, `DateOfJoin`, and `Description`. The table includes a student record containing the student's name and AWS user ARN in `Description`.

## Authentication

Amazon Cognito is configured with Managed Login, a public application client, no client secret, OAuth 2.0 Authorization Code Grant, and PKCE. API Gateway validates the Cognito token before invoking the backend Lambda.

## IAM

The backend Lambda uses an IAM execution role with the DynamoDB permissions required for the employee lookup. AWS credentials are not included in the source code.

## Deployment and Testing

The application was deployed using AWS Lambda, API Gateway, DynamoDB, Cognito, and IAM. Testing covered:

- Application access
- Cognito authentication
- Valid employee lookup
- Student employee lookup
- Invalid Employee ID
- Unauthorized API access

## Source Files

- `ui_lambda.py` – Returns the user interface and handles Cognito login.
- `backend_lambda.py` – Retrieves employee records from DynamoDB.

## AI Assistance

AI assistance was used to write the Lambda code and configure Cognito authentication and PKCE.(ChatGPT)
