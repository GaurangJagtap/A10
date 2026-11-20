"""Data preparation module for Breast Cancer Wisconsin dataset.

Prepares tabular train/test splits formatted for both local training
and AWS SageMaker tabular training jobs.
"""

import os
import argparse
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split


def load_and_prepare_data(
    data_dir: str = "data",
    test_size: float = 0.2,
    random_state: int = 42
):
    """Load breast cancer dataset, perform stratified split, and save CSV files.

    SageMaker tabular training convention:
    - SageMaker built-in algorithms (and standard containers) typically expect
      the target variable to be the first column, without headers in raw input mode,
      or with headers in custom Scikit-Learn script mode.
    - We save:
        1) X_train.csv, X_test.csv (features only, 30 columns)
        2) y_train.csv, y_test.csv (labels only: 0 = malignant, 1 = benign)
        3) train.csv, test.csv (combined dataset with target as the first column,
           standard for SageMaker S3 ingestion)
    """
    os.makedirs(data_dir, exist_ok=True)

    cancer = load_breast_cancer(as_frame=True)
    features = cancer.data
    target = cancer.target

    # Stratified 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        stratify=target,
        random_state=random_state
    )

    # Save feature sets
    X_train_path = os.path.join(data_dir, "X_train.csv")
    X_test_path = os.path.join(data_dir, "X_test.csv")
    y_train_path = os.path.join(data_dir, "y_train.csv")
    y_test_path = os.path.join(data_dir, "y_test.csv")

    X_train.to_csv(X_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_train.to_csv(y_train_path, index=False, header=["target"])
    y_test.to_csv(y_test_path, index=False, header=["target"])

    # Combined datasets (target as first column for standard SageMaker format)
    train_combined = pd.concat([y_train.rename("target"), X_train], axis=1)
    test_combined = pd.concat([y_test.rename("target"), X_test], axis=1)

    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")

    train_combined.to_csv(train_path, index=False)
    test_combined.to_csv(test_path, index=False)

    print(f"Data preparation completed successfully.")
    print(f"Features: {X_train.shape[1]} columns")
    print(f"Training samples: {X_train.shape[0]}")
    print(f"Testing samples: {X_test.shape[0]}")
    print(f"Files saved to '{data_dir}/': X_train.csv, X_test.csv, y_train.csv, y_test.csv, train.csv, test.csv")

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Wisconsin Breast Cancer data")
    parser.add_argument("--data-dir", type=str, default="data", help="Output directory for CSV files")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set fraction")
    parser.add_argument("--random-state", type=int, default=42, help="Random state seed")
    args = parser.parse_args()

    load_and_prepare_data(
        data_dir=args.data_dir,
        test_size=args.test_size,
        random_state=args.random_state
    )
