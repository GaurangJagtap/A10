# Screenshot Manifest: Simulated AWS MLOps Deployment

This manifest documents the visual demonstration assets for Assignment 9.
All visual assets illustrate the **local simulation** of AWS services using real local model training and real local predictions.

> **CRITICAL NOTICE**: In strict accordance with assignment constraints, these represent local simulation outputs and logs. They do NOT contain fabricated AWS Console UI screenshots or counterfeit AWS credentials.

---

## Required Visual Artifacts & Demonstrations

| # | Component | Target Artifact / Log Output | Command to Produce Output | Description |
|---|---|---|---|---|
| **01** | **Simulated S3 Bucket** | Console output & staging directory showing `train.csv` and `test.csv` with byte counts and `s3://` URIs | `python scripts/simulate_aws_pipeline.py` (Step 2) | Demonstrates data staging under `s3://simulated-mlops-breast-cancer-bucket/breast-cancer/data/` |
| **02** | **Simulated IAM Roles** | Policy JSON definitions and least-privilege explanations | `python -c "import json; from src.simulated_iam import get_simulated_iam_roles; print(json.dumps(get_simulated_iam_roles(), indent=2))"` | Details SageMaker & Lambda execution roles and permission policies |
| **03** | **Simulated SageMaker Training** | Console execution logs and `.simulated_aws/simulated_training_job.json` | `python scripts/simulate_aws_pipeline.py` (Step 4 & 5) | Displays hyperparameters, local execution duration, and evaluation metrics |
| **04** | **Simulated Model Artifact** | `model.tar.gz` archive details (size, timestamp, archive contents) | `tar -ztvf .simulated_aws/s3/simulated-mlops-breast-cancer-bucket/breast-cancer/output/model.tar.gz` | Shows `model.joblib` packaged inside standard SageMaker tarball |
| **05** | **Simulated SageMaker Endpoint** | Endpoint status (`InService`), feature dimension (30), and live model binding | `python scripts/simulate_aws_pipeline.py` (Step 7) | Confirms endpoint is ready to accept 30-feature vector inputs |
| **06** | **Simulated AWS Lambda** | Request parsing, 30-feature validation, and response body | `python scripts/simulate_aws_pipeline.py` (Step 8) | Shows JSON response (`prediction: 0/1`, `label: malignant/benign`) |
| **07** | **Simulated API Gateway** | Local HTTP server execution & curl / Invoke-RestMethod response | `python src/local_api.py` followed by `Invoke-RestMethod` | Shows `POST /predict` returning prediction and handling bad inputs (400) |
| **08** | **Simulated CloudWatch Metrics & Logs** | JSON metrics summary and `.simulated_aws/cloudwatch/simulated_cloudwatch.log` | `python scripts/simulate_aws_pipeline.py` (Step 10) | Tracks invocations, latency breakdowns, and 5XX alarm state |
| **09** | **Simulated Cleanup** | Teardown logs confirming removal of staging assets | `python scripts/simulate_aws_pipeline.py` (Step 11) | Demonstrates safe cleanup of simulated resources without altering repository data |
| **10** | **Complete Test Suite** | Pytest summary showing all unit and simulation tests passing | `pytest -v` | Complete 23-test validation across unit, model, lambda, and simulation |

---

## Screenshot Capture Guidelines for College Submission

When submitting terminal screenshots for Assignment 9:
1. Ensure the terminal header displays `ASSIGNMENT 9: AWS ML DEPLOYMENT LOCAL PIPELINE SIMULATION`.
2. Capture the complete step sequence from Step 1 to Step 11 by running:
   ```powershell
   python scripts/simulate_aws_pipeline.py
   ```
3. Capture the passing test suite:
   ```powershell
   pytest -v
   ```
4. Save terminal screenshots in this directory (`screenshots/`) named `01_s3_staging.png`, `02_training_job.png`, `03_evaluation_metrics.png`, etc.
