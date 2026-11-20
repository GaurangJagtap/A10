"""Generate visual figures and screenshots for the assignment report."""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("screenshots", exist_ok=True)

# 1. Architecture Diagram
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Title
    ax.text(6, 5.6, "End-to-End MLOps AWS Deployment Architecture (Local Simulation)", 
            ha="center", va="center", fontsize=15, fontweight="bold", color="#1A365D")

    # Boxes
    boxes = [
        {"x": 0.5, "y": 3.0, "w": 2.2, "h": 1.5, "title": "Client / User", "desc": "POST /predict\nJSON payload\n(30 Features)", "color": "#EBF8FF", "ec": "#3182CE"},
        {"x": 3.2, "y": 3.0, "w": 2.3, "h": 1.5, "title": "API Gateway\n(127.0.0.1:8000)", "desc": "HTTP Routing\nCORS Handling\nPayload Validation", "color": "#FEFCBF", "ec": "#D69E2E"},
        {"x": 6.0, "y": 3.0, "w": 2.4, "h": 1.5, "title": "AWS Lambda\nIntegration Layer", "desc": "30-Feature Parsing\nError Handling (400/502)\nEndpoint Invocation", "color": "#FEEBC8", "ec": "#DD6B20"},
        {"x": 9.0, "y": 3.0, "w": 2.5, "h": 1.5, "title": "SageMaker Endpoint\n(simulated-rf-endpoint)", "desc": "Random Forest Model\nBinary Classification\nClass Probability", "color": "#C6F6D5", "ec": "#38A169"},
        {"x": 2.0, "y": 0.6, "w": 3.2, "h": 1.4, "title": "Amazon S3 Staging", "desc": "train.csv, test.csv\nmodel.tar.gz artifact\nStorage Versioning", "color": "#E9D8FD", "ec": "#805AD5"},
        {"x": 6.5, "y": 0.6, "w": 4.5, "h": 1.4, "title": "CloudWatch Monitoring & IAM", "desc": "Invocations, Latency, 5XX Alarms\nStructured Logs (.simulated_aws/)\nLeast Privilege IAM Roles", "color": "#FED7D7", "ec": "#E53E3E"},
    ]

    for b in boxes:
        rect = patches.FancyBboxPatch(
            (b["x"], b["y"]), b["w"], b["h"],
            boxstyle="round,pad=0.1", fc=b["color"], ec=b["ec"], lw=2
        )
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.35, b["title"],
                ha="center", va="center", fontsize=10, fontweight="bold", color="#2D3748")
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"]/2 - 0.2, b["desc"],
                ha="center", va="center", fontsize=8, color="#4A5568")

    # Arrows
    arrow_props = dict(arrowstyle="->", lw=2, color="#2B6CB0")
    ax.annotate("", xy=(3.2, 3.75), xytext=(2.7, 3.75), arrowprops=arrow_props)
    ax.annotate("", xy=(6.0, 3.75), xytext=(5.5, 3.75), arrowprops=arrow_props)
    ax.annotate("", xy=(9.0, 3.75), xytext=(8.4, 3.75), arrowprops=arrow_props)

    # Dotted connections to S3 and CloudWatch
    dash_props = dict(arrowstyle="<->", lw=1.5, ls="--", color="#718096")
    ax.annotate("", xy=(3.6, 2.0), xytext=(3.6, 3.0), arrowprops=dash_props)
    ax.annotate("", xy=(7.2, 2.0), xytext=(7.2, 3.0), arrowprops=dash_props)
    ax.annotate("", xy=(10.2, 2.0), xytext=(10.2, 3.0), arrowprops=dash_props)

    plt.tight_layout()
    output_path = "screenshots/architecture_diagram.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Created: {output_path}")

# 2. Confusion Matrix & ROC Curve Figure
def create_confusion_matrix_roc():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

    # Confusion Matrix
    cm = np.array([[39, 3], [2, 70]])
    im = ax1.imshow(cm, cmap="Blues", interpolation="nearest")
    ax1.set_title("Confusion Matrix (Test Set N=114)", fontsize=11, fontweight="bold")
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(["Malignant (0)", "Benign (1)"], fontsize=9)
    ax1.set_yticklabels(["Malignant (0)", "Benign (1)"], fontsize=9)
    ax1.set_xlabel("Predicted Label", fontsize=10, fontweight="bold")
    ax1.set_ylabel("True Label", fontsize=10, fontweight="bold")

    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > 30 else "black"
            ax1.text(j, i, str(cm[i, j]), ha="center", va="center",
                     fontsize=14, fontweight="bold", color=color)

    plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)

    # Performance Metrics Bar Chart
    metrics = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    scores = [0.9561, 0.9589, 0.9722, 0.9655, 0.9937]
    bars = ax2.bar(metrics, scores, color=["#3182CE", "#38A169", "#DD6B20", "#805AD5", "#D69E2E"], width=0.55)
    ax2.set_ylim(0.85, 1.02)
    ax2.set_title("Random Forest Evaluation Metrics", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Score", fontsize=10, fontweight="bold")
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.005, f"{h:.4f}",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax2.tick_params(axis="x", rotation=15)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    output_path = "screenshots/model_evaluation_metrics.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Created: {output_path}")

create_architecture_diagram()
create_confusion_matrix_roc()
