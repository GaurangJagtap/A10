"""Generate the complete Assignment 9 Word Report Document."""

import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set internal cell margins."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()

    # Page Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Style definitions
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)

    # -------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------
    # VIT Header Table with Logo
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    header_table.columns[0].width = Inches(1.4)
    header_table.columns[1].width = Inches(5.1)

    # Logo in col 0
    logo_path = "C:/College/SEM 5/MLOPs/Assignment_8/vit_logo.jpeg"
    cell_logo = header_table.cell(0, 0)
    p_logo = cell_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(logo_path):
        p_logo.add_run().add_picture(logo_path, width=Inches(1.2))

    # Institute title in col 1
    cell_inst = header_table.cell(0, 1)
    p_inst = cell_inst.paragraphs[0]
    p_inst.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r1 = p_inst.add_run("Bansilal Ramnath Agarwal Charitable Trust's\n")
    r1.font.size = Pt(11)
    r1.font.bold = False
    r2 = p_inst.add_run("Vishwakarma Institute of Technology, Pune\n")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
    r3 = p_inst.add_run("(An Autonomous Institute Affiliated to Savitribai Phule Pune University)\n")
    r3.font.size = Pt(9.5)
    r3.font.italic = True
    r4 = p_inst.add_run("Department of Artificial Intelligence and Data Science")
    r4.font.size = Pt(11.5)
    r4.font.bold = True
    r4.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Student Details Table
    meta_table = doc.add_table(rows=13, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(2.3)
    meta_table.columns[1].width = Inches(4.2)

    meta_rows = [
        ("Department", "Artificial Intelligence and Data Science"),
        ("Student Name", "Gaurang"),
        ("Class", "TY (Third Year B.Tech)"),
        ("Division", "B"),
        ("Roll No", "[Roll Number]"),
        ("PRN NO", "[PRN Number]"),
        ("Semester", "Semester V (Sem 5)"),
        ("Academic Year", "2026-27"),
        ("Subject Name & Code", "MLOps (AI3206C)"),
        ("Assignment No.", "9"),
        ("Title of Assignment", "Train and Deploy a Machine Learning Model using AWS SageMaker (Local Simulation & MLOps Architecture)"),
        ("Date of Performance", "20/11/2026"),
        ("Date of Submission", "21/11/2026")
    ]

    for idx, (label, val) in enumerate(meta_rows):
        row = meta_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.text = label
        c1.text = val
        p0 = c0.paragraphs[0]
        p0.runs[0].font.bold = True
        p0.runs[0].font.size = Pt(10)
        p1 = c1.paragraphs[0]
        p1.runs[0].font.size = Pt(10)
        set_cell_background(c0, "F7FAFC" if idx % 2 == 0 else "EDF2F7")
        set_cell_background(c1, "FFFFFF" if idx % 2 == 0 else "F7FAFC")
        set_cell_margins(c0, top=70, bottom=70, left=120, right=120)
        set_cell_margins(c1, top=70, bottom=70, left=120, right=120)

    doc.add_page_break()

    # Helper function for headings
    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(title)
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
        return p

    def add_sub_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(title)
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
        return p

    # -------------------------------------------------------------
    # AIM
    # -------------------------------------------------------------
    add_sec_heading("Aim")
    p = doc.add_paragraph(
        "To design, develop, test, and evaluate an end-to-end Machine Learning deployment pipeline "
        "using AWS SageMaker, Amazon S3, AWS Lambda, Amazon API Gateway, and Amazon CloudWatch for a "
        "Breast Cancer Wisconsin classification model, executing the entire workflow through a verified, "
        "cost-safe, and fully reproducible local AWS simulation."
    )
    p.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # PROBLEM STATEMENT
    # -------------------------------------------------------------
    add_sec_heading("Problem Statement")
    p = doc.add_paragraph(
        "Deploying machine learning models into enterprise production requires robust operational architecture "
        "spanning cloud object storage (S3), secure least-privilege identity delegation (IAM), managed model training "
        "and real-time inference endpoints (SageMaker), serverless integration layers (AWS Lambda), managed REST API "
        "gateways (API Gateway), and real-time operational telemetry and alarms (CloudWatch). "
        "However, developing and debugging cloud MLOps pipelines directly on public cloud infrastructure incurs "
        "significant billable costs, requires credential management risks, and lacks rapid local debuggability. "
        "Hence, there is a vital need to build a comprehensive, modular local MLOps pipeline that reliably prepares "
        "Wisconsin Breast Cancer tabular datasets (30 numeric features), trains a Random Forest classifier, serializes "
        "standard SageMaker model artifacts (model.tar.gz), exposes a validated REST API endpoint, records operational "
        "latency and telemetry, and runs an automated 11-stage local AWS simulation without creating billable cloud resources."
    )
    p.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # OBJECTIVES
    # -------------------------------------------------------------
    add_sec_heading("Objectives")
    objs = [
        "CO1: Understand the enterprise cloud MLOps deployment lifecycle spanning model training, artifact packaging, endpoint hosting, and serverless integration.",
        "CO2: Prepare and structure tabular training datasets into stratified splits adhering strictly to AWS SageMaker target-first CSV ingestion requirements.",
        "CO3: Formulate least-privilege IAM policies and execution role definitions for SageMaker training containers and AWS Lambda integration handlers.",
        "CO4: Implement modular, SageMaker script-mode compatible model training (train.py) and inference hooks (model_fn, input_fn, predict_fn, output_fn).",
        "CO5: Develop and validate an AWS Lambda proxy integration layer that validates exactly 30 numeric features and formats CORS-compliant JSON responses.",
        "CO6: Implement local operational observability tracking API invocations, latency percentiles, error distribution (4XX/5XX), and CloudWatch alarm triggers.",
        "CO7: Verify the complete MLOps workflow through an automated 11-stage local simulation and comprehensive unit testing (23 tests)."
    ]
    for obj in objs:
        p = doc.add_paragraph(obj, style='List Bullet')
        p.paragraph_format.space_after = Pt(2)

    # -------------------------------------------------------------
    # TOOLS, TECHNOLOGIES AND ENVIRONMENT
    # -------------------------------------------------------------
    add_sec_heading("Tools, Technologies and Environment")
    env_table = doc.add_table(rows=7, cols=2)
    env_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    env_table.autofit = False
    env_table.columns[0].width = Inches(2.2)
    env_table.columns[1].width = Inches(4.3)

    env_data = [
        ("Operating System", "Windows 11 / PowerShell 5.1 & 7.x"),
        ("Programming Language", "Python 3.12.10 (virtual environment .venv)"),
        ("Machine Learning Framework", "Scikit-Learn 1.9+, Pandas 3.1+, NumPy 2.5+, Joblib 1.6+"),
        ("Testing & Quality Assurance", "Pytest 9.2+ (23 Unit and Integration Tests)"),
        ("AWS SDK & Cloud Simulation", "Boto3 1.44+, Botocore 1.44+, Python HTTP Server"),
        ("Dataset / Machine Learning Model", "Breast Cancer Wisconsin Diagnostic (569 samples, 30 numeric features) / RandomForestClassifier (100 trees)"),
        ("Cloud / MLOps Architecture", "Amazon S3, AWS SageMaker (Script Mode), AWS Lambda, Amazon API Gateway, CloudWatch (Local Simulated)")
    ]

    for idx, (item, detail) in enumerate(env_data):
        row = env_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.text = item
        c1.text = detail
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c0, "EDF2F7")
        set_cell_background(c1, "FFFFFF" if idx % 2 == 0 else "F7FAFC")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # BACKGROUND THEORY
    # -------------------------------------------------------------
    add_sec_heading("Background Theory")

    add_sub_heading("a) Introduction to the Concept")
    doc.add_paragraph(
        "Machine Learning Operations (MLOps) represents the intersection of machine learning, software engineering, "
        "and DevOps. Its primary goal is to standardize and automate the delivery of machine learning models into reliable "
        "production environments. In classical software engineering, continuous delivery automates testing and deployment "
        "of binary code. In machine learning, continuous delivery must also account for model artifacts, training scripts, "
        "changing data distributions, and real-time inferencing latencies.\n"
        "AWS SageMaker provides an end-to-end managed ecosystem covering distributed model training, model registry, and "
        "real-time auto-scaling endpoints. When deployed in enterprise environments, SageMaker endpoints are typically fronted "
        "by AWS Lambda (acting as a serverless anti-corruption and validation layer) and exposed via Amazon API Gateway "
        "to client applications. Amazon CloudWatch provides telemetry by continuously tracking invocation volume, error status, "
        "and model latency percentiles."
    )

    add_sub_heading("b) Why This Cloud Architecture?")
    doc.add_paragraph(
        "1. Decoupled Architecture: Clients communicate with Amazon API Gateway, which enforces rate limiting, SSL termination, "
        "and request schema validation without exposing internal infrastructure.\n"
        "2. Serverless Integration: AWS Lambda parses incoming JSON payloads, validates the presence and numerical format of "
        "features, and transforms requests before invoking SageMaker. This prevents malformed requests from consuming expensive "
        "GPU/CPU compute on the inference endpoint.\n"
        "3. SageMaker Script Mode: Rather than using rigid black-box algorithms, SageMaker Script Mode allows ML engineers to write "
        "standard Scikit-Learn code (train.py, inference.py) that executes identically in local development environments and cloud "
        "Docker containers.\n"
        "4. Observability and Alarms: CloudWatch captures operational metrics (Invocations, 4XX, 5XX, ModelLatency) and raises "
        "automated alarms when error thresholds are exceeded."
    )

    add_sub_heading("c) Key Components and Terminology")
    doc.add_paragraph(
        "• Amazon S3 (Simple Storage Service): High-durability object storage holding training datasets and versioned model archives.\n"
        "• AWS IAM Execution Roles: Defines least-privilege trust and permission policies allowing SageMaker to access designated S3 "
        "buckets and allowing Lambda to invoke specific endpoint ARNs.\n"
        "• SageMaker Model Artifact (model.tar.gz): A gzip compressed tar archive containing the serialized model weights (model.joblib).\n"
        "• SageMaker Endpoint: A managed, real-time HTTP hosting container implementing model_fn, input_fn, predict_fn, and output_fn.\n"
        "• AWS Lambda Proxy Integration: Serverless compute that receives API Gateway events, validates data, and invokes endpoints.\n"
        "• CloudWatch Metrics & Log Groups: Real-time time-series database storing operational telemetry, latency breakdowns, and error states."
    )

    add_sub_heading("d) Benefits and Limitations")
    doc.add_paragraph(
        "Benefits: Elastic scalability, automated high availability, robust security via IAM separation, complete decoupling of API clients "
        "from inference compute, and unified CloudWatch monitoring.\n"
        "Limitations & Local Simulation Rationale: In academic and staging environments, provisioning active SageMaker endpoints incurs "
        "per-hour instance billing regardless of traffic. Our local simulation architecture implements a 100% locally executed simulation "
        "that mirrors the exact file structures, IAM policies, SageMaker contract hooks, and CloudWatch metrics without incurring cloud costs."
    )

    # -------------------------------------------------------------
    # ARCHITECTURE / WORKFLOW DIAGRAM
    # -------------------------------------------------------------
    add_sec_heading("Architecture / Workflow Diagram")
    doc.add_paragraph(
        "The end-to-end architecture demonstrates the complete request flow and cloud storage relationships implemented in the project:"
    )

    arch_img_path = "screenshots/architecture_diagram.png"
    if os.path.exists(arch_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(arch_img_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Figure 1: End-to-End MLOps AWS Deployment Architecture (Local Simulation Pipeline)")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(9.5)

    # -------------------------------------------------------------
    # PROCEDURE (STEP-BY-STEP IMPLEMENTATION)
    # -------------------------------------------------------------
    add_sec_heading("Procedure (Step-by-Step Implementation)")

    # Step 1
    add_sub_heading("Step 1: Dataset Acquisition and Tabular Preparation")
    doc.add_paragraph(
        "We load the Wisconsin Diagnostic Breast Cancer dataset from Scikit-Learn containing 569 instances and exactly 30 continuous features. "
        "We execute an 80/20 stratified train-test split (random_state=42) to maintain identical class ratios across partitions. "
        "To comply with AWS SageMaker tabular ingestion standards, we generate both feature/label files (X_train.csv, y_train.csv) and combined "
        "target-first files (train.csv, test.csv) where the target label occupies column 0."
    )
    doc.add_paragraph("Command: python src/prepare_data.py --data-dir data --test-size 0.2")

    # Step 2
    add_sub_heading("Step 2: Model Training and Artifact Serialization")
    doc.add_paragraph(
        "In src/train.py, we implement a RandomForestClassifier with n_estimators=100 and random_state=42. "
        "The training script is built using SageMaker Script Mode conventions, checking for the SM_CHANNEL_TRAIN and SM_MODEL_DIR environment variables "
        "while falling back seamlessly to local directory paths. The fitted model is serialized to models/model.joblib."
    )
    doc.add_paragraph("Command: python src/train.py --n-estimators 100 --random-state 42")

    # Step 3
    add_sub_heading("Step 3: Comprehensive Model Evaluation")
    doc.add_paragraph(
        "In src/evaluate.py, we evaluate model generalization against the independent test dataset (114 samples). "
        "We calculate Accuracy, Precision, Recall, F1-Score, Probability-based ROC-AUC, and the Confusion Matrix, persisting the results to metrics/evaluation.json."
    )
    doc.add_paragraph("Command: python src/evaluate.py --model-path models/model.joblib --data-dir data")

    eval_chart_path = "screenshots/model_evaluation_metrics.png"
    if os.path.exists(eval_chart_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(eval_chart_path, width=Inches(5.5))
        p_cap = doc.add_paragraph("Figure 2: Confusion Matrix and Model Evaluation Metric Performance")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(9.5)

    # Step 4
    add_sub_heading("Step 4: AWS S3 Staging and Model Artifact Packaging")
    doc.add_paragraph(
        "We simulate Amazon S3 bucket storage locally (.simulated_aws/s3/simulated-mlops-breast-cancer-bucket/). "
        "We stage train.csv (97,652 bytes) and test.csv (24,796 bytes) under breast-cancer/data/. "
        "Next, we package the local model artifact into standard SageMaker format: model.tar.gz (57,639 bytes) and stage it under breast-cancer/output/."
    )

    s3_console_img = "AWS S3 Bucket Objects Console.png"
    if os.path.exists(s3_console_img):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(s3_console_img, width=Inches(6.0))
        p_cap = doc.add_paragraph("Figure 3: AWS S3 Staged Objects Console View (Data CSVs and Model Artifacts)")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(9.5)

    # Step 5
    add_sub_heading("Step 5: Least-Privilege IAM Policy Definitions")
    doc.add_paragraph(
        "In src/simulated_iam.py, we define declarative IAM policies enforcing least privilege: "
        "1. simulated-SageMakerExecutionRole: Restricts S3 access exclusively to the designated bucket and log groups.\n"
        "2. simulated-LambdaExecutionRole: Grants permission ONLY to invoke the specific SageMaker endpoint ARN and write CloudWatch logs."
    )

    # Step 6
    add_sub_heading("Step 6: SageMaker Real-Time Endpoint Serving and Lambda Integration")
    doc.add_paragraph(
        "In src/inference.py and lambda_function/lambda_function.py, we implement the serving logic: "
        "• SageMaker container hooks: model_fn, input_fn, predict_fn, and output_fn.\n"
        "• Lambda Handler: Validates that the input payload contains exactly 30 float values, returns HTTP 400 for malformed input, "
        "and handles endpoint errors with HTTP 502."
    )

    # Step 7
    add_sub_heading("Step 7: Local API Gateway Server and CloudWatch Telemetry")
    doc.add_paragraph(
        "In src/local_api.py, we run a local HTTP server binding to 127.0.0.1:8000 exposing POST /predict. "
        "Requests are processed through the Lambda integration handler and operational metrics are recorded in CloudWatch format: "
        "Invocations, Total Latency, Model Latency, Overhead Latency, and an automated 5XX Error Alarm."
    )

    # Step 8
    add_sub_heading("Step 8: Automated 11-Stage Pipeline Simulation and Verification")
    doc.add_paragraph(
        "We execute the master orchestration script scripts/simulate_aws_pipeline.py, running the entire workflow sequentially from "
        "data preparation through simulated cleanup."
    )
    doc.add_paragraph("Command: python scripts/simulate_aws_pipeline.py")

    # Step 9
    add_sub_heading("Step 9: Comprehensive Pytest Validation")
    doc.add_paragraph(
        "We execute the full automated test suite covering data integrity, model loading, 30-feature validation, Lambda request parsing, "
        "simulated S3 staging, and cleanup. All 23 unit tests pass cleanly."
    )
    doc.add_paragraph("Command: pytest -v")

    # -------------------------------------------------------------
    # CODE / CONFIGURATION FILES
    # -------------------------------------------------------------
    add_sec_heading("Code / Configuration Files")
    doc.add_paragraph(
        "The project consists of clean, modular Python modules. The primary implementation files are summarized below:"
    )

    code_snippets = [
        ("1. Data Preparation (src/prepare_data.py)",
"""cancer = load_breast_cancer(as_frame=True)
features, target = cancer.data, cancer.target
X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.2, stratify=target, random_state=42
)
train_combined = pd.concat([y_train.rename("target"), X_train], axis=1)
train_combined.to_csv("data/train.csv", index=False)"""),

        ("2. Lambda Handler (lambda_function/lambda_function.py)",
"""def lambda_handler(event, context=None, sagemaker_client=None):
    is_valid, features, err_msg = validate_payload(event)
    if not is_valid:
        return create_response(400, {"status": "error", "message": err_msg})
    endpoint_name = os.environ.get("SAGEMAKER_ENDPOINT_NAME")
    payload_bytes = json.dumps({"features": features}).encode("utf-8")
    response = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=payload_bytes
    )
    return create_response(200, {"status": "success", "result": json.loads(response["Body"].read())})"""),

        ("3. Central Simulation Configuration (src/simulation_config.py)",
"""@dataclass(frozen=True)
class SimulatedAWSConfig:
    simulation_mode: bool = True
    simulated_region: str = "simulated-us-east-1"
    simulated_s3_bucket: str = "simulated-mlops-breast-cancer-bucket"
    simulated_sagemaker_endpoint_name: str = "simulated-rf-breast-cancer-endpoint"
    local_api_url: str = "http://127.0.0.1:8000/predict"
    simulated_cloudwatch_alarm_name: str = "simulated-High5xxErrorRateAlarm" """)
    ]

    for title, code in code_snippets:
        add_sub_heading(title)
        p = doc.add_paragraph()
        run = p.add_run(code)
        run.font.name = 'Consolas'
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_after = Pt(6)

    doc.add_paragraph("GitHub Repository Link: https://github.com/GaurangJagtap/A10")

    # -------------------------------------------------------------
    # OUTPUT / RESULTS
    # -------------------------------------------------------------
    add_sec_heading("Output / Results")
    doc.add_paragraph(
        "The local simulation was verified across all functional stages. Below is the quantitative performance and operational telemetry summary:"
    )

    res_table = doc.add_table(rows=8, cols=3)
    res_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_table.autofit = False
    res_table.columns[0].width = Inches(2.2)
    res_table.columns[1].width = Inches(2.0)
    res_table.columns[2].width = Inches(2.3)

    res_headers = ["Metric / Parameter", "Observed Value", "Status / Operational Assessment"]
    for i, h in enumerate(res_headers):
        c = res_table.rows[0].cells[i]
        c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c, "2B6CB0")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)

    results_data = [
        ("Model Accuracy", "95.61% (109 / 114 test samples)", "High Generalization (> 90% threshold)"),
        ("Model Precision & Recall", "Precision: 95.89% | Recall: 97.22%", "Balanced False Positive / Negative Rate"),
        ("F1-Score & ROC-AUC", "F1: 96.55% | ROC-AUC: 99.37%", "Near-optimal Discriminative Capacity"),
        ("Confusion Matrix", "TN: 39, FP: 3, FN: 2, TP: 70", "Only 5 misclassifications out of 114"),
        ("Model Training Duration", "0.21 seconds (Local Execution)", "High Efficiency Random Forest"),
        ("Simulated CloudWatch Latency", "Model: 35.6 ms | Overhead: 0.41 ms", "Sub-50ms Production Inference"),
        ("Pytest Test Suite", "23 Passed / 0 Failed (2.62s)", "100% Component & Integration Pass Rate")
    ]

    for idx, (m, v, s) in enumerate(results_data):
        row = res_table.rows[idx + 1]
        for c_i, text in enumerate([m, v, s]):
            c = row.cells[c_i]
            c.text = text
            c.paragraphs[0].runs[0].font.size = Pt(9.0)
            set_cell_background(c, "FFFFFF" if idx % 2 == 0 else "F7FAFC")
            set_cell_margins(c, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # OBSERVATIONS AND ANALYSIS
    # -------------------------------------------------------------
    add_sec_heading("Observations and Analysis")
    obs = [
        "1. SageMaker Tabular Format Compliance: SageMaker built-in tabular algorithms and Scikit-Learn script containers enforce that target labels occupy the first column (column 0) without index columns. Generating train.csv and test.csv in this exact layout guarantees smooth transition to cloud S3 ingestion.",
        "2. Serverless Lambda Decoupling: Implementing AWS Lambda as an intermediate validation proxy effectively filters invalid client payloads (e.g. truncated feature vectors or string values) returning HTTP 400 immediately, protecting the SageMaker endpoint from unnecessary inference load.",
        "3. High Model Discriminative Performance: The Random Forest classifier achieved a ROC-AUC score of 0.9937 and an overall accuracy of 95.61% on unseen test data, proving that 30 cellular characteristics provide excellent diagnostic predictive power.",
        "4. Operational Telemetry and 5XX Alarm: In simulated CloudWatch, average model latency was observed at 35.6 ms with an overhead latency of 0.41 ms. The simulated 5XX alarm remained in the OK state during normal operation and transitioned to ALARM when threshold errors were induced.",
        "5. Cost and Security Safeguards: Performing the complete architecture validation locally eliminated AWS billable resource charges, avoided credential leakage risks, and enabled rapid iterative debugging of the entire MLOps lifecycle."
    ]
    for o in obs:
        p = doc.add_paragraph(o)
        p.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # CONCLUSION
    # -------------------------------------------------------------
    add_sec_heading("Conclusion")
    doc.add_paragraph(
        "Thus, we have successfully designed, implemented, evaluated, and verified an end-to-end Machine Learning deployment pipeline "
        "using AWS SageMaker, Amazon S3, AWS Lambda, Amazon API Gateway, and Amazon CloudWatch for Breast Cancer Wisconsin diagnosis. "
        "Through an innovative, 100% local AWS simulation architecture, all 11 stages of the cloud MLOps workflow—including dataset staging, "
        "least-privilege IAM policies, script-mode training, model.tar.gz packaging, endpoint serving, serverless Lambda validation, "
        "and CloudWatch telemetry—were validated with 23 passing tests without incurring cloud expenses or credential vulnerabilities. "
        "This project establishes a production-grade blueprint for scalable, secure, and observable cloud machine learning deployments."
    )

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    add_sec_heading("References")
    refs = [
        "[1] Amazon Web Services, 'Use Scikit-learn with the SageMaker Python SDK', AWS Documentation, https://docs.aws.amazon.com/sagemaker/latest/dg/sklearn.html, accessed 20/11/2026.",
        "[2] Amazon Web Services, 'Call an Amazon SageMaker model endpoint using Amazon API Gateway and AWS Lambda', AWS Architecture Center, https://aws.amazon.com/blogs/machine-learning/call-an-amazon-sagemaker-model-endpoint-using-amazon-api-gateway-and-aws-lambda/, accessed 20/11/2026.",
        "[3] Scikit-learn Developers, 'Breast Cancer Wisconsin (Diagnostic) Dataset', Scikit-learn 1.9 Documentation, https://scikit-learn.org/stable/datasets/toy_dataset.html#breast-cancer-dataset, accessed 20/11/2026.",
        "[4] Amazon Web Services, 'Monitoring Amazon SageMaker with Amazon CloudWatch', AWS Documentation, https://docs.aws.amazon.com/sagemaker/latest/dg/monitoring-cloudwatch.html, accessed 20/11/2026."
    ]
    for r in refs:
        p = doc.add_paragraph(r)
        p.paragraph_format.space_after = Pt(2)
        p.runs[0].font.size = Pt(9.5)

    # Save document
    output_filename = "MLOps_Assignment_9_AWS_ML_Deployment_Report.docx"
    doc.save(output_filename)
    print(f"Report successfully generated and saved to: {output_filename}")

create_report()
