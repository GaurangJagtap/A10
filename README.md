# Breast Cancer Classification – AWS MLOps Deployment & Local Simulation

Comprehensive implementation for **Assignment 9: Train and Deploy a Machine Learning Model using AWS SageMaker**.

> **IMPORTANT NOTICE**: This project features a **100% Local AWS Pipeline Simulation**. No billable cloud resources were created, no AWS account credentials were used or requested, and no actual cloud endpoints were deployed. All simulated services are explicitly labeled `SIMULATED`.

---

## 1. Assignment Objective & Architecture

The objective is to train a Random Forest classification model on the Breast Cancer Wisconsin dataset (30 numeric features) and demonstrate the full cloud MLOps workflow:

```
[Client / HTTP POST]
        │
        ▼
[Amazon API Gateway]      --> Localhost HTTP Server (127.0.0.1:8000/predict)
        │
        ▼
[AWS Lambda Function]     --> Lambda Handler (Validates exactly 30 features)
        │
        ▼
[Amazon SageMaker]        --> Local Endpoint / Inference Module (model.joblib)
        │
        ▼
[Amazon CloudWatch]       --> Local CloudWatch Simulator (Metrics, Logs, Alarms)
```

### Key Workflow Stages Demonstrated:
1. **S3 Storage**: Staging dataset (`train.csv`, `test.csv`) and model artifacts (`model.tar.gz`).
2. **IAM Roles**: Least-privilege role policies for SageMaker training and Lambda invocation.
3. **SageMaker Training**: Training `RandomForestClassifier` and measuring execution time.
4. **Model Evaluation**: Comprehensive metrics (Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix).
5. **Artifact Packaging**: Serializing `model.joblib` and packaging as standard `model.tar.gz`.
6. **SageMaker Endpoint**: In-process model serving with health check and 30-feature validation.
7. **Lambda Integration**: Event payload validation, error propagation, and response serialization.
8. **API Gateway**: Exposing a local `POST /predict` HTTP endpoint.
9. **CloudWatch Monitoring**: Real-time tracking of Invocations, Latency, Errors, and 5XX Alarm triggers.
10. **Cleanup**: Automated teardown of simulation staging assets.

---

## 2. Dataset & Model Details

- **Dataset**: Scikit-Learn Wisconsin Breast Cancer (`sklearn.datasets.load_breast_cancer`).
- **Features**: Exactly 30 numeric dimensions (mean, error, and worst metrics for cell nuclei).
- **Target**: Binary classification (`0` = Malignant, `1` = Benign).
- **Split**: 80% Train (455 samples) / 20% Test (114 samples), stratified by target with `random_state=42`.
- **Classifier**: `RandomForestClassifier(n_estimators=100, random_state=42)`.
- **Actual Evaluation Metrics**:
  - **Accuracy**: `0.9561`
  - **Precision**: `0.9589`
  - **Recall**: `0.9722`
  - **F1 Score**: `0.9655`
  - **ROC-AUC**: `0.9924`
  - **Confusion Matrix**: `[[39, 3], [2, 70]]` (TN: 39, FP: 3, FN: 2, TP: 70)

---

## 3. Repository Structure

```text
mlops-aws-deployment/
│
├── data/                               # Prepared dataset CSVs
│   ├── X_train.csv / X_test.csv        # 30-feature datasets
│   ├── y_train.csv / y_test.csv        # Labels
│   ├── train.csv / test.csv            # SageMaker standard target-first format
│
├── src/                                # Core ML & Simulation logic
│   ├── prepare_data.py                 # Data fetching and stratified split
│   ├── train.py                        # Model training (SageMaker script-mode compatible)
│   ├── evaluate.py                     # Evaluation metrics (includes ROC-AUC)
│   ├── inference.py                    # Inference validation & SageMaker hooks (model_fn, etc.)
│   ├── simulation_config.py            # Central simulated AWS configuration
│   ├── simulated_iam.py                # Simulated least-privilege IAM policies
│   ├── local_aws_simulator.py          # Local simulator for S3, SageMaker, CloudWatch, Cleanup
│   └── local_api.py                    # Local HTTP server simulating API Gateway (POST /predict)
│
├── lambda_function/                    # AWS Lambda integration layer
│   ├── lambda_function.py              # Handler (validates 30 features, invokes endpoint)
│   └── requirements.txt                # Lambda package requirements (boto3)
│
├── tests/                              # Comprehensive test suite (23 tests)
│   ├── test_data.py                    # Data preparation tests
│   ├── test_model.py                   # Model training, inference, and ROC-AUC evaluation tests
│   ├── test_lambda.py                  # Lambda parsing, validation, and error tests
│   └── test_simulation.py             # Complete tests for S3, IAM, CloudWatch, API, and Cleanup
│
├── scripts/
│   ├── validate_environment.py         # Validates local Python dependencies
│   └── simulate_aws_pipeline.py        # Master orchestrator for the 11-step local simulation
│
├── screenshots/
│   └── README.md                       # Screenshot manifest & presentation guidelines
│
├── models/
│   └── model.joblib                    # Trained local model artifact
├── metrics/
│   └── evaluation.json                 # Evaluation metrics in JSON format
├── requirements.txt                    # Local dependencies
├── pytest.ini                          # Pytest configuration
├── deployment-notes.md                 # Simulation map & real AWS migration placeholders
└── README.md                           # Project documentation
```

---

## 4. How to Run the Project

### A. Environment Setup
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Verify environment
python scripts/validate_environment.py
```

### B. Run the Full End-to-End Simulation
To execute the complete 11-stage simulated AWS workflow:
```powershell
python scripts/simulate_aws_pipeline.py
```
This runs all stages sequentially:
`Data Prep -> S3 Staging -> IAM Verification -> Training Job -> Evaluation -> Artifact Packaging -> Endpoint Serving -> Lambda Invocation -> API Gateway Testing -> CloudWatch Logging -> Cleanup`.

### C. Run the Local API Gateway Server
To interact with the model via a live localhost HTTP endpoint:
```powershell
python src/local_api.py
```
Send a prediction request in another PowerShell terminal:
```powershell
$body = @{
    features = @(
        17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871,
        1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193,
        25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -Body $body -ContentType "application/json"
```

### D. Run All Unit & Simulation Tests
```powershell
pytest -v
```

---

## 5. Screenshot Manifest & Demonstration Checklist

To capture presentation screenshots for college submission, refer to [screenshots/README.md](file:///c:/College/SEM%205/MLOPs/mlops-aws-deployment/screenshots/README.md).
The manifest covers:
1. Simulated S3 Bucket Staging
2. Simulated IAM Policy Definitions
3. Simulated SageMaker Training Job & Output Metrics
4. Model Artifact Packaging (`model.tar.gz`)
5. Simulated Endpoint Status (`InService`)
6. Lambda Invocation Execution
7. API Gateway Request/Response Logs (Valid & 400 cases)
8. CloudWatch Operational Summary & 5XX Alarm
9. Simulated Cleanup Teardown
10. Full Pytest Execution (23 Passing Tests)
