"""Inference module for Breast Cancer Wisconsin classification.

Provides model loading, input validation for exactly 30 numeric features,
and prediction functions suitable for local prediction and AWS SageMaker endpoints.
"""

import os
from typing import Any, Dict, List, Union
import joblib
import numpy as np

# Wisconsin breast cancer dataset feature count & class labels
EXPECTED_FEATURE_COUNT = 30
CLASS_MAPPING = {
    0: "malignant",
    1: "benign"
}


def load_model(model_path: str = "models/model.joblib"):
    """Load model artifact from disk."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model artifact not found at {model_path}")
    return joblib.load(model_path)


def validate_input(features: Union[List[Any], np.ndarray]) -> np.ndarray:
    """Validate that input consists of exactly 30 numeric values.

    Args:
        features: 1D or 2D list/array containing feature values.

    Returns:
        np.ndarray: Validated 2D float64 array of shape (N, 30).

    Raises:
        ValueError: If feature count or types are invalid.
    """
    if features is None:
        raise ValueError("Input features cannot be None.")

    try:
        arr = np.array(features, dtype=np.float64)
    except (ValueError, TypeError) as e:
        raise ValueError(f"All 30 features must be valid numeric values. Error: {str(e)}")

    if arr.ndim == 1:
        if arr.shape[0] != EXPECTED_FEATURE_COUNT:
            raise ValueError(
                f"Expected {EXPECTED_FEATURE_COUNT} features, received {arr.shape[0]}."
            )
        arr = arr.reshape(1, -1)
    elif arr.ndim == 2:
        if arr.shape[1] != EXPECTED_FEATURE_COUNT:
            raise ValueError(
                f"Expected {EXPECTED_FEATURE_COUNT} features per sample, received {arr.shape[1]}."
            )
    else:
        raise ValueError(f"Input array must be 1D or 2D, received dimension {arr.ndim}.")

    if np.isnan(arr).any():
        raise ValueError("Input features contain NaN (null) values.")
    if np.isinf(arr).any():
        raise ValueError("Input features contain infinite values.")

    return arr


def predict(features: Union[List[Any], np.ndarray], model: Any = None, model_path: str = "models/model.joblib") -> List[Dict[str, Any]]:
    """Generate predictions for validated input.

    Args:
        features: Input feature list or array.
        model: Pre-loaded model (optional).
        model_path: Path to model artifact if model is not provided.

    Returns:
        List of dicts with binary prediction and readable class label.
    """
    if model is None:
        model = load_model(model_path)

    validated_features = validate_input(features)
    preds = model.predict(validated_features)
    probs = model.predict_proba(validated_features) if hasattr(model, "predict_proba") else None

    results = []
    for idx, pred in enumerate(preds):
        pred_int = int(pred)
        item = {
            "prediction": pred_int,
            "label": CLASS_MAPPING.get(pred_int, "unknown"),
        }
        if probs is not None:
            item["probability"] = {
                "malignant": float(probs[idx][0]),
                "benign": float(probs[idx][1])
            }
        results.append(item)

    return results


# --- AWS SageMaker standard inference entrypoints ---
def model_fn(model_dir: str):
    """SageMaker endpoint model loading handler."""
    model_path = os.path.join(model_dir, "model.joblib")
    return joblib.load(model_path)


def input_fn(request_body: str, request_content_type: str = "application/json"):
    """SageMaker endpoint input deserializer and validator."""
    import json
    if request_content_type == "application/json":
        data = json.loads(request_body)
        if isinstance(data, dict) and "features" in data:
            return validate_input(data["features"])
        elif isinstance(data, list):
            return validate_input(data)
        raise ValueError("JSON request must contain a 'features' key or a list of 30 numbers.")
    raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data: np.ndarray, model: Any):
    """SageMaker endpoint prediction handler."""
    return model.predict(input_data)


def output_fn(prediction: np.ndarray, accept: str = "application/json"):
    """SageMaker endpoint output serializer."""
    import json
    results = [
        {"prediction": int(p), "label": CLASS_MAPPING.get(int(p), "unknown")}
        for p in prediction
    ]
    return json.dumps({"predictions": results}), accept
