"""Simulated IAM policy and role definitions.

Illustrates least-privilege permissions for SageMaker and Lambda execution roles.
No real AWS IAM roles or credentials are created or accessed.
"""

from typing import Dict, Any


def get_simulated_iam_roles() -> Dict[str, Any]:
    """Return simulated IAM role definitions illustrating the principle of least privilege."""
    return {
        "simulated_sagemaker_role": {
            "role_name": "simulated-SageMakerExecutionRole",
            "arn": "arn:aws:iam::000000000000:role/simulated-SageMakerExecutionRole",
            "trust_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "sagemaker.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "permissions_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "SimulatedS3DataReadWriteAccess",
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            "arn:aws:s3:::simulated-mlops-breast-cancer-bucket",
                            "arn:aws:s3:::simulated-mlops-breast-cancer-bucket/*"
                        ]
                    },
                    {
                        "Sid": "SimulatedCloudWatchLogsAccess",
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:log-group:/aws/sagemaker/*"
                    }
                ]
            },
            "least_privilege_explanation": (
                "Constrained strictly to the designated simulated S3 training/artifact bucket "
                "and SageMaker CloudWatch log groups. Does not permit broad S3 or AdministratorAccess."
            )
        },
        "simulated_lambda_role": {
            "role_name": "simulated-LambdaExecutionRole",
            "arn": "arn:aws:iam::000000000000:role/simulated-LambdaExecutionRole",
            "trust_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "permissions_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "SimulatedSageMakerInvokeEndpointOnly",
                        "Effect": "Allow",
                        "Action": "sagemaker:InvokeEndpoint",
                        "Resource": "arn:aws:sagemaker:*:*:endpoint/simulated-rf-breast-cancer-endpoint"
                    },
                    {
                        "Sid": "SimulatedCloudWatchLogsWrite",
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/simulated-breast-cancer-predict-function:*"
                    }
                ]
            },
            "least_privilege_explanation": (
                "Permits ONLY invocation of the specific simulated breast cancer endpoint "
                "and writing execution logs to its designated log group. No read/write access to S3 or IAM."
            )
        }
    }
