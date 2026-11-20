"""Simulated AWS Configuration for Local Demonstration.

All identifiers are explicitly labeled as SIMULATED.
No actual AWS resources, credentials, or billable infrastructure are used.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass(frozen=True)
class SimulatedAWSConfig:
    # General Simulation Meta
    simulation_mode: bool = True
    simulated_region: str = "simulated-us-east-1"
    
    # Simulated S3 Configuration
    simulated_s3_bucket: str = "simulated-mlops-breast-cancer-bucket"
    simulated_s3_prefix_data: str = "breast-cancer/data"
    simulated_s3_prefix_models: str = "breast-cancer/output"
    simulated_s3_train_uri: str = "s3://simulated-mlops-breast-cancer-bucket/breast-cancer/data/train.csv"
    simulated_s3_test_uri: str = "s3://simulated-mlops-breast-cancer-bucket/breast-cancer/data/test.csv"
    simulated_s3_model_tar_uri: str = "s3://simulated-mlops-breast-cancer-bucket/breast-cancer/output/model.tar.gz"
    
    # Simulated IAM Roles (Least Privilege Representation)
    simulated_sagemaker_role_arn: str = "arn:aws:iam::000000000000:role/simulated-SageMakerExecutionRole"
    simulated_lambda_role_arn: str = "arn:aws:iam::000000000000:role/simulated-LambdaExecutionRole"
    
    # Simulated SageMaker Training & Serving
    simulated_training_job_name: str = "simulated-rf-breast-cancer-training-job-001"
    simulated_sagemaker_endpoint_name: str = "simulated-rf-breast-cancer-endpoint"
    simulated_endpoint_status: str = "InService"
    simulated_instance_type: str = "ml.m5.large (simulated)"
    
    # Simulated Lambda & API Gateway
    simulated_lambda_function_name: str = "simulated-breast-cancer-predict-function"
    simulated_api_gateway_id: str = "simulated-api-01"
    simulated_api_stage: str = "prod"
    local_api_host: str = "127.0.0.1"
    local_api_port: int = 8000
    local_api_url: str = "http://127.0.0.1:8000/predict"
    
    # Simulated CloudWatch
    simulated_cloudwatch_log_group_lambda: str = "/aws/lambda/simulated-breast-cancer-predict-function"
    simulated_cloudwatch_log_group_sagemaker: str = "/aws/sagemaker/Endpoints/simulated-rf-breast-cancer-endpoint"
    simulated_cloudwatch_alarm_name: str = "simulated-High5xxErrorRateAlarm"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Default singleton instance
SIMULATED_CONFIG = SimulatedAWSConfig()
