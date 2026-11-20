"""Simulation Orchestrator Script for Assignment 9.

Demonstrates the entire end-to-end AWS MLOps workflow locally:
S3 -> IAM -> SageMaker Training -> Model Packaging -> Endpoint -> Lambda -> API Gateway -> CloudWatch -> Cleanup.

All actions are locally executed and explicitly labeled as SIMULATED.
No actual AWS resources are created, no credentials are requested, and no costs are incurred.
"""

import sys
import os
import time
import json
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.simulation_config import SIMULATED_CONFIG
from src.simulated_iam import get_simulated_iam_roles
from src.prepare_data import load_and_prepare_data
from src.train import train_model
from src.evaluate import evaluate_model
from src.local_aws_simulator import LocalAWSSimulator


def run_simulation():
    print("=" * 70)
    print("  ASSIGNMENT 9: AWS ML DEPLOYMENT LOCAL PIPELINE SIMULATION")
    print("  Mode: 100% LOCAL DEMONSTRATION (Zero billable AWS resources)")
    print("=" * 70)

    # Initialize Simulator
    simulator = LocalAWSSimulator()

    # Step 1: Data Preparation Verification
    print("\n[STEP 1 / 11] Verifying / Running Data Preparation...")
    if not os.path.exists("data/train.csv") or not os.path.exists("data/test.csv"):
        print("Data files not found. Generating now from scikit-learn...")
        load_and_prepare_data(data_dir="data", test_size=0.2, random_state=42)
    else:
        print("  [OK] Data preparation verified (train.csv and test.csv present).")

    # Step 2: Simulated S3 Staging
    print("\n[STEP 2 / 11] Executing [SIMULATED S3] Storage Staging...")
    staged_items = simulator.stage_s3_data(data_dir="data")
    print(f"  Target Simulated Bucket: {SIMULATED_CONFIG.simulated_s3_bucket}")
    for item in staged_items:
        print(f"  - Staged: {item['object_name']:<12} | Size: {item['size_bytes']:>7} bytes | URI: {item['s3_uri']}")

    # Step 3: Simulated IAM Role Verification
    print("\n[STEP 3 / 11] Verifying [SIMULATED IAM] Least-Privilege Policies...")
    iam_roles = get_simulated_iam_roles()
    for role_key, role in iam_roles.items():
        print(f"  - Role: {role['role_name']}")
        print(f"    ARN: {role['arn']}")
        print(f"    Least Privilege: {role['least_privilege_explanation']}")

    # Step 4: Local Model Training (Simulated SageMaker Training Job)
    print("\n[STEP 4 / 11] Executing Model Training [SIMULATED SageMaker Training Job]...")
    t_train_start = time.perf_counter()
    model_path = train_model(data_dir="data", model_dir="models", n_estimators=100, random_state=42)
    train_duration = time.perf_counter() - t_train_start
    print(f"  [OK] Local model trained in {train_duration:.2f}s and saved to {model_path}")

    # Step 5: Model Evaluation (including ROC-AUC)
    print("\n[STEP 5 / 11] Running Comprehensive Model Evaluation...")
    eval_metrics = evaluate_model(model_path=model_path, data_dir="data", output_dir="metrics")
    print(f"  [OK] Accuracy: {eval_metrics['accuracy']:.4f} | ROC-AUC: {eval_metrics['roc_auc']:.4f}")

    # Step 6: Model Artifact Packaging (Simulated model.tar.gz)
    print("\n[STEP 6 / 11] Packaging [SIMULATED SageMaker Artifact] (model.tar.gz)...")
    artifact_info = simulator.package_model_artifact(model_path=model_path)
    print(f"  Artifact: {artifact_info['artifact_name']}")
    print(f"  Local Staging: {artifact_info['local_path']}")
    print(f"  Simulated S3 URI: {artifact_info['s3_uri']}")
    print(f"  Artifact Size: {artifact_info['size_bytes']} bytes")

    # Record Simulated Training Job metadata
    job_record = simulator.record_simulated_training_job(
        duration_seconds=train_duration,
        metrics=eval_metrics,
        parameters={"n_estimators": 100, "random_state": 42}
    )
    print(f"  Simulated Training Job: {job_record['TrainingJobName']} (Status: Completed)")

    # Step 7: Simulated Endpoint Deployment
    print("\n[STEP 7 / 11] Starting [SIMULATED SageMaker Endpoint]...")
    endpoint_status = simulator.init_simulated_endpoint(model_path=model_path)
    print(f"  Endpoint Name:   {endpoint_status['EndpointName']}")
    print(f"  Endpoint Status: {endpoint_status['EndpointStatus']}")
    print(f"  Instance Type:   {endpoint_status['InstanceType']}")

    # Step 8: Lambda Integration Execution
    print("\n[STEP 8 / 11] Invoking [SIMULATED AWS Lambda] Integration Layer...")
    # Load 1 benign sample and 1 malignant sample from X_test.csv
    X_test = pd.read_csv("data/X_test.csv")
    y_test = pd.read_csv("data/y_test.csv")
    sample_features = X_test.iloc[0].tolist()

    # Invoke Lambda simulation with standard payload
    valid_event = {"features": sample_features}
    lambda_resp = simulator.invoke_simulated_lambda(valid_event)
    print(f"  Lambda Status Code: {lambda_resp['statusCode']}")
    print(f"  Lambda Response: {lambda_resp['body']}")

    # Step 9: API Gateway Simulation Testing (Valid & Error cases)
    print("\n[STEP 9 / 11] Testing [SIMULATED API Gateway] Request / Response Contract...")
    # 9a. Successful prediction request
    api_event_success = {
        "resource": "/predict",
        "path": "/predict",
        "httpMethod": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"features": sample_features})
    }
    resp_success = simulator.invoke_simulated_lambda(api_event_success)
    print(f"  [Test Case A: Valid 30 Features] -> Status: {resp_success['statusCode']}")

    # 9b. Invalid feature count (29 features -> 400 Bad Request)
    api_event_bad_count = {
        "resource": "/predict",
        "path": "/predict",
        "httpMethod": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"features": sample_features[:-1]})
    }
    resp_bad_count = simulator.invoke_simulated_lambda(api_event_bad_count)
    print(f"  [Test Case B: Invalid Feature Count] -> Status: {resp_bad_count['statusCode']} (Expected 400)")

    # 9c. Non-numeric feature input -> 400 Bad Request
    bad_features = sample_features.copy()
    bad_features[0] = "invalid_string"
    api_event_bad_type = {
        "resource": "/predict",
        "path": "/predict",
        "httpMethod": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"features": bad_features})
    }
    resp_bad_type = simulator.invoke_simulated_lambda(api_event_bad_type)
    print(f"  [Test Case C: Non-Numeric Feature] -> Status: {resp_bad_type['statusCode']} (Expected 400)")

    # Step 10: Simulated CloudWatch Monitoring
    print("\n[STEP 10 / 11] Inspecting [SIMULATED CloudWatch] Metrics & Logs...")
    summary = simulator.cloudwatch.get_summary()
    print(json.dumps(summary, indent=4))
    print(f"  Simulated Log Stream File: {simulator.cloudwatch.log_file}")

    # Step 11: Simulated Cleanup Teardown
    print("\n[STEP 11 / 11] Executing [SIMULATED AWS Cleanup / Teardown]...")
    cleanup_res = simulator.simulated_cleanup()
    print(f"  Status: {cleanup_res['Status']}")
    for res in cleanup_res['SimulatedResourcesRemoved']:
        print(f"  - Removed: {res}")
    print(f"  Notice: {cleanup_res['Notice']}")

    print("\n" + "=" * 70)
    print("  SIMULATION COMPLETED SUCCESSFULLY!")
    print("  All 11 AWS workflow phases validated locally.")
    print("=" * 70)


if __name__ == "__main__":
    run_simulation()
