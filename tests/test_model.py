"""Unit tests for model training, evaluation, and inference."""

import os
import numpy as np
import pytest
from src.prepare_data import load_and_prepare_data
from src.train import train_model
from src.evaluate import evaluate_model
from src.inference import load_model, validate_input, predict


@pytest.fixture(scope="module")
def prepared_env(tmp_path_factory):
    """Fixture to prepare data, train model, and provide directories."""
    base_dir = tmp_path_factory.mktemp("ml_pipeline")
    data_dir = str(base_dir / "data")
    model_dir = str(base_dir / "models")
    metrics_dir = str(base_dir / "metrics")

    # Step 1: Prepare data
    load_and_prepare_data(data_dir=data_dir, test_size=0.2, random_state=42)

    # Step 2: Train model
    model_path = train_model(
        data_dir=data_dir,
        model_dir=model_dir,
        n_estimators=50,
        random_state=42
    )

    return {
        "data_dir": data_dir,
        "model_dir": model_dir,
        "model_path": model_path,
        "metrics_dir": metrics_dir
    }


def test_model_training_and_loading(prepared_env):
    """Test model file creation and loading."""
    model_path = prepared_env["model_path"]
    assert os.path.exists(model_path)
    model = load_model(model_path)
    assert hasattr(model, "predict")
    assert hasattr(model, "n_features_in_")
    assert model.n_features_in_ == 30


def test_model_evaluation(prepared_env):
    """Test evaluation metrics computation."""
    res = evaluate_model(
        model_path=prepared_env["model_path"],
        data_dir=prepared_env["data_dir"],
        output_dir=prepared_env["metrics_dir"]
    )
    assert "accuracy" in res
    assert "precision" in res
    assert "recall" in res
    assert "f1_score" in res
    assert "roc_auc" in res
    assert "confusion_matrix" in res
    # Breast cancer with RF typically scores > 90%
    assert res["accuracy"] > 0.90
    assert res["roc_auc"] > 0.90
    assert os.path.exists(os.path.join(prepared_env["metrics_dir"], "evaluation.json"))


def test_inference_valid_input(prepared_env):
    """Test prediction with exactly 30 numeric features."""
    sample_30 = [1.0] * 30
    predictions = predict(sample_30, model_path=prepared_env["model_path"])
    assert len(predictions) == 1
    assert "prediction" in predictions[0]
    assert "label" in predictions[0]
    assert predictions[0]["prediction"] in [0, 1]
    assert predictions[0]["label"] in ["malignant", "benign"]


def test_inference_invalid_feature_count():
    """Test validation fails when feature count is not 30."""
    with pytest.raises(ValueError, match="Expected 30 features"):
        validate_input([1.0] * 10)

    with pytest.raises(ValueError, match="Expected 30 features"):
        validate_input([1.0] * 35)


def test_inference_invalid_non_numeric():
    """Test validation fails on non-numeric values."""
    with pytest.raises(ValueError):
        validate_input(["invalid"] * 30)

    with pytest.raises(ValueError):
        validate_input([np.nan] * 30)


def test_inference_batch(prepared_env):
    """Test batch prediction with multiple rows of 30 features."""
    batch = np.ones((5, 30))
    predictions = predict(batch, model_path=prepared_env["model_path"])
    assert len(predictions) == 5
