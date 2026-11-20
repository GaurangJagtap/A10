"""Local AWS Cloud Services Simulator.

Provides clearly-labeled local simulations for:
- Simulated S3 (folder staging & inventory)
- Simulated SageMaker (tar.gz packaging, job metadata, in-process serving)
- Simulated CloudWatch (request logging, metrics tracking, 5XX alarm state)
- Simulated Cleanup (clearing staging without touching core repository files)

All activities operate entirely on local files with zero external AWS calls.
"""

import os
import shutil
import tarfile
import json
import time
from typing import Dict, Any, List, Optional
from src.simulation_config import SIMULATED_CONFIG, SimulatedAWSConfig
from src.inference import load_model, validate_input, predict


class SimulatedCloudWatch:
    """In-memory and file-backed simulation of AWS CloudWatch."""
    def __init__(self, log_dir: str = ".simulated_aws/cloudwatch"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "simulated_cloudwatch.log")
        self.metrics = {
            "Invocations": 0,
            "SuccessCount": 0,
            "4XXErrors": 0,
            "5XXErrors": 0,
            "TotalLatencyMs": 0.0,
            "ModelLatencyMs": 0.0,
            "OverheadLatencyMs": 0.0,
            "SimulatedAlarmState": "OK"  # OK or ALARM
        }

    def record_request(
        self,
        status_code: int,
        total_latency_ms: float,
        model_latency_ms: float,
        overhead_latency_ms: float,
        message: str
    ):
        self.metrics["Invocations"] += 1
        self.metrics["TotalLatencyMs"] += total_latency_ms
        self.metrics["ModelLatencyMs"] += model_latency_ms
        self.metrics["OverheadLatencyMs"] += overhead_latency_ms

        if 200 <= status_code < 300:
            self.metrics["SuccessCount"] += 1
        elif 400 <= status_code < 500:
            self.metrics["4XXErrors"] += 1
        elif 500 <= status_code < 600:
            self.metrics["5XXErrors"] += 1

        # Check simulated 5XX alarm threshold: > 0 consecutive 5xx errors or > 2 total
        if self.metrics["5XXErrors"] >= 2:
            self.metrics["SimulatedAlarmState"] = "ALARM"
        else:
            self.metrics["SimulatedAlarmState"] = "OK"

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "logGroup": SIMULATED_CONFIG.simulated_cloudwatch_log_group_lambda,
            "statusCode": status_code,
            "totalLatencyMs": round(total_latency_ms, 2),
            "modelLatencyMs": round(model_latency_ms, 2),
            "overheadLatencyMs": round(overhead_latency_ms, 2),
            "message": message,
            "simulatedAlarmState": self.metrics["SimulatedAlarmState"]
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_summary(self) -> Dict[str, Any]:
        inv = self.metrics["Invocations"]
        avg_total = (self.metrics["TotalLatencyMs"] / inv) if inv > 0 else 0.0
        avg_model = (self.metrics["ModelLatencyMs"] / inv) if inv > 0 else 0.0
        avg_overhead = (self.metrics["OverheadLatencyMs"] / inv) if inv > 0 else 0.0

        return {
            "simulation_label": "SIMULATED CloudWatch Operational Metrics",
            "Invocations": self.metrics["Invocations"],
            "SuccessCount": self.metrics["SuccessCount"],
            "4XXErrors": self.metrics["4XXErrors"],
            "5XXErrors": self.metrics["5XXErrors"],
            "AverageTotalLatencyMs": round(avg_total, 2),
            "AverageModelLatencyMs": round(avg_model, 2),
            "AverageOverheadLatencyMs": round(avg_overhead, 2),
            "SimulatedAlarm": {
                "AlarmName": SIMULATED_CONFIG.simulated_cloudwatch_alarm_name,
                "State": self.metrics["SimulatedAlarmState"],
                "Threshold": "5XXErrors >= 2"
            }
        }


class LocalAWSSimulator:
    """Manages the lifecycle of the local AWS simulation."""

    def __init__(self, base_sim_dir: str = ".simulated_aws", config: SimulatedAWSConfig = SIMULATED_CONFIG):
        self.base_dir = base_sim_dir
        self.config = config
        self.s3_dir = os.path.join(self.base_dir, "s3", self.config.simulated_s3_bucket)
        self.cloudwatch = SimulatedCloudWatch(os.path.join(self.base_dir, "cloudwatch"))
        self._endpoint_model = None

    def stage_s3_data(self, data_dir: str = "data") -> List[Dict[str, Any]]:
        """Stage training and testing CSVs into simulated S3 bucket."""
        s3_data_dir = os.path.join(self.s3_dir, self.config.simulated_s3_prefix_data)
        os.makedirs(s3_data_dir, exist_ok=True)

        staged_items = []
        for filename in ["train.csv", "test.csv"]:
            src_file = os.path.join(data_dir, filename)
            if not os.path.exists(src_file):
                raise FileNotFoundError(f"Source file {src_file} does not exist. Run data preparation first.")
            dest_file = os.path.join(s3_data_dir, filename)
            shutil.copy2(src_file, dest_file)
            size_bytes = os.path.getsize(dest_file)
            s3_uri = f"s3://{self.config.simulated_s3_bucket}/{self.config.simulated_s3_prefix_data}/{filename}"
            staged_items.append({
                "object_name": filename,
                "s3_uri": s3_uri,
                "local_staged_path": dest_file,
                "size_bytes": size_bytes,
                "status": "SIMULATED_S3_UPLOADED"
            })
        return staged_items

    def package_model_artifact(self, model_path: str = "models/model.joblib") -> Dict[str, Any]:
        """Package model.joblib into model.tar.gz and stage into simulated S3 bucket."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at {model_path}. Train model first.")

        s3_model_dir = os.path.join(self.s3_dir, self.config.simulated_s3_prefix_models)
        os.makedirs(s3_model_dir, exist_ok=True)
        tar_path = os.path.join(s3_model_dir, "model.tar.gz")

        # Create tar.gz containing model.joblib
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(model_path, arcname="model.joblib")

        stat = os.stat(tar_path)
        return {
            "artifact_name": "model.tar.gz",
            "s3_uri": self.config.simulated_s3_model_tar_uri,
            "local_path": tar_path,
            "size_bytes": stat.st_size,
            "created_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)),
            "status": "SIMULATED_ARTIFACT_PACKAGED"
        }

    def record_simulated_training_job(
        self,
        duration_seconds: float,
        metrics: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a simulated SageMaker training job execution record."""
        if parameters is None:
            parameters = {"n_estimators": 100, "random_state": 42, "n_jobs": -1}

        job_record = {
            "SimulationLabel": "SIMULATED SageMaker Training Job Record",
            "TrainingJobName": self.config.simulated_training_job_name,
            "TrainingJobStatus": "Completed",
            "RoleArn": self.config.simulated_sagemaker_role_arn,
            "TrainingStartTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - duration_seconds)),
            "TrainingEndTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "TrainingDurationSeconds": round(duration_seconds, 2),
            "HyperParameters": parameters,
            "InputDataConfig": [
                {
                    "ChannelName": "train",
                    "DataSource": {"S3Uri": self.config.simulated_s3_train_uri}
                },
                {
                    "ChannelName": "test",
                    "DataSource": {"S3Uri": self.config.simulated_s3_test_uri}
                }
            ],
            "OutputDataConfig": {
                "S3OutputPath": f"s3://{self.config.simulated_s3_bucket}/{self.config.simulated_s3_prefix_models}/"
            },
            "ModelArtifactS3Uri": self.config.simulated_s3_model_tar_uri,
            "FinalEvaluationMetrics": metrics
        }

        # Save metadata record
        meta_file = os.path.join(self.base_dir, "simulated_training_job.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(job_record, f, indent=4)

        return job_record

    def init_simulated_endpoint(self, model_path: str = "models/model.joblib") -> Dict[str, Any]:
        """Initialize in-process simulated endpoint using the actual trained model."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path {model_path} not found.")
        self._endpoint_model = load_model(model_path)
        
        status_info = {
            "SimulationLabel": "SIMULATED SageMaker Endpoint",
            "EndpointName": self.config.simulated_sagemaker_endpoint_name,
            "EndpointStatus": self.config.simulated_endpoint_status,
            "InstanceType": self.config.simulated_instance_type,
            "ModelSource": self.config.simulated_s3_model_tar_uri,
            "FeaturesAccepted": 30,
            "ReadyForInference": True
        }
        return status_info

    def invoke_simulated_endpoint(self, features: List[float]) -> Dict[str, Any]:
        """Perform inference on the simulated SageMaker endpoint."""
        if self._endpoint_model is None:
            raise RuntimeError("Simulated endpoint is not in service. Initialize it first.")

        t0 = time.perf_counter()
        predictions = predict(features, model=self._endpoint_model)
        model_latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "predictions": predictions,
            "_model_latency_ms": model_latency_ms
        }

    def invoke_simulated_lambda(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Lambda function invocation wrapping the local endpoint.

        Emits metrics to simulated CloudWatch.
        """
        t_start = time.perf_counter()
        
        # Mock SageMaker client invoking the local endpoint
        class SimulatedSageMakerClientWrapper:
            def __init__(self, simulator_instance):
                self.sim = simulator_instance

            def invoke_endpoint(self, EndpointName, ContentType, Accept, Body):
                if EndpointName != self.sim.config.simulated_sagemaker_endpoint_name:
                    raise ValueError(f"Endpoint {EndpointName} not found.")
                payload = json.loads(Body.decode("utf-8"))
                result = self.sim.invoke_simulated_endpoint(payload["features"])
                
                class MockBody:
                    def __init__(self, data):
                        self.data = json.dumps(data).encode("utf-8")
                    def read(self):
                        return self.data
                
                return {
                    "Body": MockBody(result),
                    "_model_latency_ms": result["_model_latency_ms"]
                }

        from lambda_function.lambda_function import lambda_handler

        # Ensure environment variable is set
        os.environ["SAGEMAKER_ENDPOINT_NAME"] = self.config.simulated_sagemaker_endpoint_name

        client_wrapper = SimulatedSageMakerClientWrapper(self)
        response = lambda_handler(event, sagemaker_client=client_wrapper)

        total_latency_ms = (time.perf_counter() - t_start) * 1000.0
        # If response was successful, extract model latency from body
        model_latency_ms = 0.0
        if response.get("statusCode") == 200:
            try:
                body_data = json.loads(response["body"])
                model_latency_ms = body_data.get("result", {}).get("_model_latency_ms", total_latency_ms * 0.7)
            except Exception:
                model_latency_ms = total_latency_ms * 0.7
        
        overhead_latency_ms = max(0.0, total_latency_ms - model_latency_ms)

        # Record into simulated CloudWatch
        status_code = response.get("statusCode", 500)
        msg = f"HTTP {status_code} response generated by simulated Lambda."
        self.cloudwatch.record_request(
            status_code=status_code,
            total_latency_ms=total_latency_ms,
            model_latency_ms=model_latency_ms,
            overhead_latency_ms=overhead_latency_ms,
            message=msg
        )

        return response

    def simulated_cleanup(self) -> Dict[str, Any]:
        """Perform simulated teardown of staging assets without deleting project files."""
        items_removed = []
        if os.path.exists(self.s3_dir):
            shutil.rmtree(self.s3_dir)
            items_removed.append(f"Simulated S3 Bucket ({self.config.simulated_s3_bucket})")

        self._endpoint_model = None
        items_removed.append(f"Simulated Endpoint ({self.config.simulated_sagemaker_endpoint_name})")

        return {
            "SimulationLabel": "SIMULATED AWS Teardown / Cleanup",
            "Status": "CLEANUP_COMPLETED",
            "SimulatedResourcesRemoved": items_removed,
            "Notice": "Local source files, data/ and models/ remain untouched."
        }
