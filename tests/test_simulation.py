"""Unit tests for the Local AWS Simulation components."""

import os
import json
import pytest
from src.simulation_config import SIMULATED_CONFIG, SimulatedAWSConfig
from src.simulated_iam import get_simulated_iam_roles
from src.local_aws_simulator import LocalAWSSimulator, SimulatedCloudWatch


@pytest.fixture
def sim_fixture(tmp_path):
    """Fixture providing an isolated LocalAWSSimulator in a temp folder."""
    sim_dir = str(tmp_path / "sim_aws")
    config = SimulatedAWSConfig()
    sim = LocalAWSSimulator(base_sim_dir=sim_dir, config=config)
    return sim, sim_dir


def test_simulation_config():
    """Verify simulation configuration properties and safe defaults."""
    cfg = SIMULATED_CONFIG
    assert cfg.simulation_mode is True
    assert "simulated" in cfg.simulated_region
    assert "simulated" in cfg.simulated_s3_bucket
    assert "simulated" in cfg.simulated_sagemaker_endpoint_name
    assert cfg.local_api_port == 8000


def test_simulated_iam_roles():
    """Verify simulated IAM least-privilege role definitions."""
    roles = get_simulated_iam_roles()
    assert "simulated_sagemaker_role" in roles
    assert "simulated_lambda_role" in roles
    
    sm_role = roles["simulated_sagemaker_role"]
    assert "sagemaker.amazonaws.com" in json.dumps(sm_role["trust_policy"])
    assert "least_privilege_explanation" in sm_role

    lm_role = roles["simulated_lambda_role"]
    assert "lambda.amazonaws.com" in json.dumps(lm_role["trust_policy"])
    assert "sagemaker:InvokeEndpoint" in json.dumps(lm_role["permissions_policy"])


def test_simulated_s3_staging(sim_fixture):
    """Verify local S3 staging of train.csv and test.csv."""
    sim, sim_dir = sim_fixture
    staged = sim.stage_s3_data(data_dir="data")
    assert len(staged) == 2
    for item in staged:
        assert os.path.exists(item["local_staged_path"])
        assert item["size_bytes"] > 0
        assert item["status"] == "SIMULATED_S3_UPLOADED"


def test_model_artifact_packaging(sim_fixture):
    """Verify packaging of model.joblib into model.tar.gz."""
    sim, sim_dir = sim_fixture
    artifact = sim.package_model_artifact(model_path="models/model.joblib")
    assert artifact["artifact_name"] == "model.tar.gz"
    assert os.path.exists(artifact["local_path"])
    assert artifact["size_bytes"] > 0
    assert "s3://" in artifact["s3_uri"]


def test_simulated_endpoint_and_lambda(sim_fixture):
    """Verify simulated SageMaker endpoint and Lambda invocation integration."""
    sim, sim_dir = sim_fixture
    endpoint_status = sim.init_simulated_endpoint(model_path="models/model.joblib")
    assert endpoint_status["EndpointStatus"] == "InService"
    assert endpoint_status["ReadyForInference"] is True

    # Test valid 30 features
    event = {"features": [1.0] * 30}
    response = sim.invoke_simulated_lambda(event)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert "result" in body
    assert len(body["result"]["predictions"]) == 1


def test_simulated_api_gateway_validation(sim_fixture):
    """Verify simulated API Gateway payload validation and error status codes."""
    sim, sim_dir = sim_fixture
    sim.init_simulated_endpoint(model_path="models/model.joblib")

    # Missing features key
    bad_event = {"body": json.dumps({"wrong_key": [1.0] * 30})}
    resp = sim.invoke_simulated_lambda(bad_event)
    assert resp["statusCode"] == 400

    # Wrong feature count (25 features instead of 30)
    bad_count = {"body": json.dumps({"features": [1.0] * 25})}
    resp = sim.invoke_simulated_lambda(bad_count)
    assert resp["statusCode"] == 400


def test_simulated_cloudwatch_metrics(sim_fixture):
    """Verify simulated CloudWatch tracking and alarm thresholds."""
    sim, sim_dir = sim_fixture
    cw = sim.cloudwatch

    # Record normal requests
    cw.record_request(200, 15.0, 10.0, 5.0, "Success")
    cw.record_request(400, 2.0, 0.0, 2.0, "Bad Request")
    summary = cw.get_summary()

    assert summary["Invocations"] == 2
    assert summary["SuccessCount"] == 1
    assert summary["4XXErrors"] == 1
    assert summary["SimulatedAlarm"]["State"] == "OK"

    # Trigger simulated alarm by recording two 5XX errors
    cw.record_request(500, 5.0, 0.0, 5.0, "Server Error 1")
    cw.record_request(500, 5.0, 0.0, 5.0, "Server Error 2")
    summary_alarm = cw.get_summary()
    assert summary_alarm["5XXErrors"] == 2
    assert summary_alarm["SimulatedAlarm"]["State"] == "ALARM"


def test_simulated_cleanup(sim_fixture):
    """Verify simulated cleanup removes simulated assets while leaving local files intact."""
    sim, sim_dir = sim_fixture
    sim.stage_s3_data(data_dir="data")
    assert os.path.exists(sim.s3_dir)

    cleanup_res = sim.simulated_cleanup()
    assert cleanup_res["Status"] == "CLEANUP_COMPLETED"
    assert not os.path.exists(sim.s3_dir)

    # Core files must remain untouched
    assert os.path.exists("data/train.csv")
    assert os.path.exists("models/model.joblib")
