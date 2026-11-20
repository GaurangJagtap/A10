# AWS MLOps Deployment Notes

This document contains configuration tracking, environment placeholders for future real AWS deployment, and documentation of the **Local AWS Simulation Architecture** developed for Assignment 9.

> **CRITICAL NOTICE**: In accordance with project boundaries, no billable cloud resources, AWS credentials, or real cloud accounts are accessed. All simulated components are explicitly prefixed with `simulated-`.

---

## 1. Local AWS Simulation Configuration

The local simulation mirrors the real AWS workflow without incurring cloud costs:

| Component | Simulated Resource Identifier | Local Simulation Mechanism |
| :--- | :--- | :--- |
| **Simulation Mode** | `Enabled (100% Local)` | In-process execution with zero external calls |
| **Simulated AWS Region** | `simulated-us-east-1` | Configuration label |
| **Simulated S3 Bucket** | `simulated-mlops-breast-cancer-bucket` | Local directory: `.simulated_aws/s3/` |
| **Simulated Train Data S3 URI** | `s3://simulated-mlops-breast-cancer-bucket/breast-cancer/data/train.csv` | File staged from `data/train.csv` |
| **Simulated Test Data S3 URI** | `s3://simulated-mlops-breast-cancer-bucket/breast-cancer/data/test.csv` | File staged from `data/test.csv` |
| **Simulated Model Artifact** | `s3://simulated-mlops-breast-cancer-bucket/breast-cancer/output/model.tar.gz` | Actual local tarball packaged from `models/model.joblib` |
| **Simulated SageMaker Role** | `arn:aws:iam::000000000000:role/simulated-SageMakerExecutionRole` | Defined in `src/simulated_iam.py` |
| **Simulated Lambda Role** | `arn:aws:iam::000000000000:role/simulated-LambdaExecutionRole` | Defined in `src/simulated_iam.py` |
| **Simulated Training Job** | `simulated-rf-breast-cancer-training-job-001` | Logged in `.simulated_aws/simulated_training_job.json` |
| **Simulated SageMaker Endpoint** | `simulated-rf-breast-cancer-endpoint` | In-memory local serving using `src/inference.py` |
| **Simulated Lambda Function** | `simulated-breast-cancer-predict-function` | Direct execution of `lambda_function/lambda_function.py` |
| **Local API Gateway URL** | `http://127.0.0.1:8000/predict` | Local Python HTTP server (`src/local_api.py`) |
| **Simulated CloudWatch Log** | `/aws/lambda/simulated-breast-cancer-predict-function` | Local log stream: `.simulated_aws/cloudwatch/simulated_cloudwatch.log` |
| **Simulated 5XX Alarm** | `simulated-High5xxErrorRateAlarm` | Triggered in simulation if 5XX errors >= 2 |

---

## 2. Future Real AWS Deployment Placeholders

When moving from local simulation to an actual AWS environment with an active AWS account, populate the following placeholders:

| Parameter | Configuration Placeholder | Notes / Description |
| :--- | :--- | :--- |
| **AWS Region** | `<AWS_REGION>` *(e.g., us-east-1)* | Target region for all deployed resources |
| **IAM SageMaker Execution Role** | `<SAGEMAKER_EXECUTION_ROLE_ARN>` | Role granting SageMaker S3 & CloudWatch access |
| **IAM Lambda Execution Role** | `<LAMBDA_EXECUTION_ROLE_ARN>` | Role granting Lambda permissions to invoke SageMaker |
| **S3 Bucket Name** | `<S3_BUCKET_NAME>` | Bucket storing training data, code, & model artifacts |
| **S3 Train Data URI** | `s3://<S3_BUCKET_NAME>/breast-cancer/data/train/` | Location of `train.csv` |
| **S3 Test Data URI** | `s3://<S3_BUCKET_NAME>/breast-cancer/data/test/` | Location of `test.csv` |
| **SageMaker Training Job Name** | `<SAGEMAKER_TRAINING_JOB_NAME>` | Unique training execution job name |
| **Model Artifact S3 URI** | `s3://<S3_BUCKET_NAME>/breast-cancer/output/model.tar.gz` | Trained joblib model packaged for serving |
| **SageMaker Model Name** | `<SAGEMAKER_MODEL_NAME>` | Registered model in SageMaker Model Registry |
| **SageMaker Endpoint Config** | `<SAGEMAKER_ENDPOINT_CONFIG_NAME>` | Configuration specifying instance type & model variant |
| **SageMaker Endpoint Name** | `<SAGEMAKER_ENDPOINT_NAME>` | Live real-time inference endpoint |
| **Lambda Function Name** | `<LAMBDA_FUNCTION_NAME>` | Lambda handler (`lambda_function.py`) |
| **API Gateway URL** | `https://<API_GATEWAY_ID>.execute-api.<AWS_REGION>.amazonaws.com/<STAGE>/predict` | Public REST/HTTP API endpoint |
| **CloudWatch Log Group (Lambda)** | `/aws/lambda/<LAMBDA_FUNCTION_NAME>` | Lambda logs & execution traces |
| **CloudWatch Log Group (SageMaker)** | `/aws/sagemaker/Endpoints/<SAGEMAKER_ENDPOINT_NAME>` | SageMaker endpoint logs & latency monitoring |

---

## 3. SageMaker Tabular Data Specifications

- **Container**: Scikit-learn Scikit-Learn container (`sagemaker.sklearn.estimator.SKLearn`)
- **Input Format**: CSV
- **Target Variable**: Column 0 (`target`), binary `0` (malignant), `1` (benign)
- **Features**: Columns 1 to 30 (30 mean, SE, and worst tumor metrics)
- **Header**: SageMaker script mode accepts header rows; standard built-in algorithm mode uses headless CSV.

---

## 4. Lambda Environment Configuration

To configure AWS Lambda in the deployment stage, set the following environment variable in the Lambda Console:

```bash
SAGEMAKER_ENDPOINT_NAME=<SAGEMAKER_ENDPOINT_NAME>
```

---

## 5. API Gateway Request / Response Contract

### Request
```http
POST /predict HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "features": [
    17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871,
    1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193,
    25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189
  ]
}
```

### Response
```json
{
  "status": "success",
  "endpoint": "simulated-rf-breast-cancer-endpoint",
  "result": {
    "predictions": [
      {
        "prediction": 0,
        "label": "malignant",
        "probability": {
          "malignant": 0.98,
          "benign": 0.02
        }
      }
    ]
  }
}
```
