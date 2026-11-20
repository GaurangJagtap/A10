"""Model training script for Breast Cancer classification using RandomForestClassifier.

Modularized and compatible with both local execution and future AWS SageMaker
Scikit-Learn script-mode containers.
"""

import os
import argparse
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def train_model(
    data_dir: str = "data",
    model_dir: str = "models",
    n_estimators: int = 100,
    max_depth: int = None,
    random_state: int = 42
) -> str:
    """Train RandomForestClassifier on prepared tabular data and save joblib artifact."""
    X_train_path = os.path.join(data_dir, "X_train.csv")
    y_train_path = os.path.join(data_dir, "y_train.csv")

    if not os.path.exists(X_train_path) or not os.path.exists(y_train_path):
        raise FileNotFoundError(
            f"Training data not found in '{data_dir}'. Run src/prepare_data.py first."
        )

    X_train = pd.read_csv(X_train_path)
    y_train = pd.read_csv(y_train_path).values.ravel()

    print(f"Training RandomForestClassifier with {len(X_train)} samples and {X_train.shape[1]} features...")
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    os.makedirs(model_dir, exist_ok=True)
    model_output_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_output_path)
    print(f"Model saved successfully to: {model_output_path}")

    return model_output_path


if __name__ == "__main__":
    # Support SageMaker environment variables or standard CLI flags
    default_data_dir = os.environ.get("SM_CHANNEL_TRAIN", "data")
    default_model_dir = os.environ.get("SM_MODEL_DIR", "models")

    parser = argparse.ArgumentParser(description="Train Random Forest Classifier")
    parser.add_argument("--data-dir", type=str, default=default_data_dir, help="Directory containing training CSVs")
    parser.add_argument("--model-dir", type=str, default=default_model_dir, help="Directory to save model artifact")
    parser.add_argument("--n-estimators", type=int, default=100, help="Number of trees")
    parser.add_argument("--max-depth", type=int, default=None, help="Maximum tree depth")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train_model(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=args.random_state
    )
