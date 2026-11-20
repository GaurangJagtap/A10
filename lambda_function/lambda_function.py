"""AWS Lambda integration handler for SageMaker endpoint inference.

Receives API Gateway or direct Lambda JSON events, validates exactly 30 features,
invokes an AWS SageMaker endpoint via boto3, and returns formatted responses.
Does not hardcode any credentials, regions, or endpoint names.
"""

import json
import os
from typing import Any, Dict, List, Tuple

# Expected constants
EXPECTED_FEATURE_COUNT = 30
CLASS_MAPPING = {
    0: "malignant",
    1: "benign"
}


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Format response compatible with API Gateway proxy integration."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }


def validate_payload(event: Dict[str, Any]) -> Tuple[bool, Any, str]:
    """Extract and validate the 30 input features from the incoming event.

    Supports:
      1) API Gateway payload (where body is a JSON string)
      2) Direct Lambda invocation (where event contains dict or features directly)

    Expected format:
      {"features": [v1, v2, ..., v30]}
      or
      {"body": "{\"features\": [v1, v2, ..., v30]}"}
    """
    if not isinstance(event, dict):
        return False, None, "Invalid event: expected a JSON object."

    payload = event
    if "body" in event and event["body"] is not None:
        if isinstance(event["body"], str):
            try:
                payload = json.loads(event["body"])
            except json.JSONDecodeError:
                return False, None, "Invalid JSON format in request body."
        elif isinstance(event["body"], dict):
            payload = event["body"]

    if not isinstance(payload, dict):
        return False, None, "Payload must be a JSON object containing 'features'."

    if "features" not in payload:
        return False, None, "Missing required key 'features' in payload."

    raw_features = payload["features"]
    if not isinstance(raw_features, list):
        return False, None, "'features' must be a list of numbers."

    if len(raw_features) != EXPECTED_FEATURE_COUNT:
        return False, None, (
            f"Invalid feature count: expected {EXPECTED_FEATURE_COUNT} features, "
            f"got {len(raw_features)}."
        )

    validated_features = []
    for idx, val in enumerate(raw_features):
        if isinstance(val, bool) or val is None:
            return False, None, f"Feature at index {idx} must be a valid number."
        try:
            float_val = float(val)
            validated_features.append(float_val)
        except (ValueError, TypeError):
            return False, None, f"Feature at index {idx} ('{val}') is not numeric."

    return True, validated_features, ""


def lambda_handler(event: Dict[str, Any], context: Any = None, sagemaker_client: Any = None) -> Dict[str, Any]:
    """Lambda function entry point.

    Args:
        event: Lambda invocation event (from API Gateway or direct).
        context: Lambda context object.
        sagemaker_client: Optional injected boto3 client for testing/mocking.
    """
    # 1. Validate Input
    is_valid, features, err_msg = validate_payload(event)
    if not is_valid:
        return create_response(400, {
            "status": "error",
            "message": err_msg
        })

    # 2. Get SageMaker endpoint name from environment variable
    endpoint_name = os.environ.get("SAGEMAKER_ENDPOINT_NAME")
    if not endpoint_name:
        return create_response(500, {
            "status": "error",
            "message": "Server configuration error: SAGEMAKER_ENDPOINT_NAME environment variable not set."
        })

    # 3. Initialize boto3 SageMaker runtime client if not injected
    if sagemaker_client is None:
        import boto3
        sagemaker_client = boto3.client("sagemaker-runtime")

    # 4. Invoke SageMaker Endpoint
    try:
        payload_bytes = json.dumps({"features": features}).encode("utf-8")
        response = sagemaker_client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Accept="application/json",
            Body=payload_bytes
        )

        response_body = response["Body"].read().decode("utf-8")
        sagemaker_result = json.loads(response_body)

        # Standardize return format
        return create_response(200, {
            "status": "success",
            "endpoint": endpoint_name,
            "result": sagemaker_result
        })

    except Exception as e:
        return create_response(502, {
            "status": "error",
            "message": f"Failed to invoke SageMaker endpoint: {str(e)}"
        })
