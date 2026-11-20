"""Unit tests for dataset preparation (src/prepare_data.py)."""

import os
import pandas as pd
import pytest
from src.prepare_data import load_and_prepare_data


def test_data_preparation_outputs(tmp_path):
    """Test that CSV files are generated with expected shapes and columns."""
    out_dir = str(tmp_path / "data")
    X_train, X_test, y_train, y_test = load_and_prepare_data(
        data_dir=out_dir,
        test_size=0.2,
        random_state=42
    )

    # 1. Total samples in breast cancer dataset is 569
    assert len(X_train) + len(X_test) == 569
    assert len(y_train) + len(y_test) == 569

    # 2. 80/20 split: 455 train, 114 test
    assert len(X_train) == 455
    assert len(X_test) == 114

    # 3. Exactly 30 features
    assert X_train.shape[1] == 30
    assert X_test.shape[1] == 30

    # 4. Check files created on disk
    expected_files = ["X_train.csv", "X_test.csv", "y_train.csv", "y_test.csv", "train.csv", "test.csv"]
    for f in expected_files:
        p = os.path.join(out_dir, f)
        assert os.path.exists(p), f"Missing expected file {f}"

    # 5. Check combined train.csv format for SageMaker (target column first, 31 columns total)
    train_combined = pd.read_csv(os.path.join(out_dir, "train.csv"))
    assert train_combined.columns[0] == "target"
    assert train_combined.shape == (455, 31)

    # 6. Stratified ratio should be preserved
    y_all_train_benign = (y_train == 1).mean()
    y_all_test_benign = (y_test == 1).mean()
    assert abs(y_all_train_benign - y_all_test_benign) < 0.05
