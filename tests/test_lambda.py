"""Unit tests for AWS Lambda handler (lambda_function/lambda_function.py)."""

import io
import json
import pytest
from lambda_function.lambda_function import lambda_handler, validate_payload


class MockStreamingBody:
    """Mock boto3 botocore response streaming body."""
    def __init__(self, data: str):
        self._data = data

    def read(self):
        return self._data.encode("utf-8")


class MockSageMakerClient:
    """Mock boto3 SageMaker runtime client."""
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.invoked_with = None

    def invoke_endpoint(self, EndpointName, ContentType, Accept, Body):
        self.invoked_with = {
            "EndpointName": EndpointName,
            "ContentType": ContentType,
            "Accept": Accept,
            "Body": Body
        }
        if self.should_fail:
            raise RuntimeError("SageMaker connection timeout")

        # Mock successful response
        response_payload = {
            "predictions": [{"prediction": 1, "label": "benign"}]
        }
        return {
            "Body": MockStreamingBody(json.dumps(response_payload))
        }


def test_validate_payload_valid_direct():
    event = {"features": [0.5] * 30}
    is_valid, features, err = validate_payload(event)
    assert is_valid is True
    assert len(features) == 30
    assert err == ""


def test_validate_payload_valid_api_gateway():
    event = {"body": json.dumps({"features": [1.2] * 30})}
    is_valid, features, err = validate_payload(event)
    assert is_valid is True
    assert len(features) == 30


def test_validate_payload_missing_features():
    event = {"body": json.dumps({"data": [1] * 30})}
    is_valid, features, err = validate_payload(event)
    assert is_valid is False
    assert "Missing required key 'features'" in err


def test_validate_payload_wrong_count():
    event = {"features": [1.0] * 29}
    is_valid, features, err = validate_payload(event)
    assert is_valid is False
    assert "expected 30 features" in err.lower()


def test_validate_payload_non_numeric():
    event = {"features": ["bad"] + [1.0] * 29}
    is_valid, features, err = validate_payload(event)
    assert is_valid is False
    assert "not numeric" in err


def test_lambda_handler_missing_env(monkeypatch):
    monkeypatch.delenv("SAGEMAKER_ENDPOINT_NAME", raising=False)
    event = {"features": [1.0] * 30}
    response = lambda_handler(event)
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["status"] == "error"
    assert "SAGEMAKER_ENDPOINT_NAME" in body["message"]


def test_lambda_handler_success(monkeypatch):
    monkeypatch.setenv("SAGEMAKER_ENDPOINT_NAME", "test-rf-endpoint")
    event = {"features": [0.5] * 30}
    mock_client = MockSageMakerClient()

    response = lambda_handler(event, sagemaker_client=mock_client)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert body["endpoint"] == "test-rf-endpoint"
    assert "result" in body
    assert mock_client.invoked_with["EndpointName"] == "test-rf-endpoint"


def test_lambda_handler_endpoint_failure(monkeypatch):
    monkeypatch.setenv("SAGEMAKER_ENDPOINT_NAME", "test-rf-endpoint")
    event = {"features": [0.5] * 30}
    mock_client = MockSageMakerClient(should_fail=True)

    response = lambda_handler(event, sagemaker_client=mock_client)
    assert response["statusCode"] == 502
    body = json.loads(response["body"])
    assert body["status"] == "error"
    assert "Failed to invoke SageMaker endpoint" in body["message"]
