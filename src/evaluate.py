"""Model evaluation script.

Calculates accuracy, precision, recall, f1-score, ROC-AUC, and confusion matrix,
prints a human-readable report, and saves evaluation metrics to JSON.
"""

import os
import json
import argparse
import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


def evaluate_model(
    model_path: str = "models/model.joblib",
    data_dir: str = "data",
    output_dir: str = "metrics"
) -> dict:
    """Evaluate trained model on test data and persist metrics to a JSON file."""
    X_test_path = os.path.join(data_dir, "X_test.csv")
    y_test_path = os.path.join(data_dir, "y_test.csv")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at '{model_path}'. Train model first.")
    if not os.path.exists(X_test_path) or not os.path.exists(y_test_path):
        raise FileNotFoundError(f"Test data not found in '{data_dir}'. Prepare data first.")

    model = joblib.load(model_path)
    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path).values.ravel()

    y_pred = model.predict(X_test)

    # Compute probabilities for class 1 (benign) for ROC-AUC
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
        roc_auc = float(roc_auc_score(y_test, y_prob))
    else:
        roc_auc = float(roc_auc_score(y_test, y_pred))

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()

    report = classification_report(
        y_test,
        y_pred,
        target_names=["malignant (0)", "benign (1)"],
        digits=4
    )

    results = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
        "target_names": ["malignant", "benign"]
    }

    print("=" * 50)
    print("MODEL EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print("\nConfusion Matrix [ [TN, FP], [FN, TP] ]:")
    print(f"  {cm[0]}")
    print(f"  {cm[1]}")
    print("\nDetailed Classification Report:")
    print(report)
    print("=" * 50)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "evaluation.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"Evaluation metrics saved to: {output_path}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate trained model")
    parser.add_argument("--model-path", type=str, default="models/model.joblib", help="Path to joblib model")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory with test files")
    parser.add_argument("--output-dir", type=str, default="metrics", help="Output directory for metrics JSON")
    args = parser.parse_args()

    evaluate_model(
        model_path=args.model_path,
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
