
import io
import sys
from pathlib import Path
from collections import Counter
from datetime import date, timedelta

import boto3
import numpy as np
import psycopg2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import dotenv_values
from scipy.stats import gaussian_kde
from sklearn.feature_extraction.text import TfidfVectorizer
import umap


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

CONFIG = dotenv_values(ROOT / ".env.local")

MODEL_ID = "apac.amazon.nova-micro-v1:0"

CATEGORIES = [
    "Infrastructure",
    "AI & Analytics",
    "Security",
]

# Keep English records separate from the Japanese dataset.
PREFIX = "[EN-DEMO2026] "

# All meeting minutes below are synthetic.
DEMO = {
    "Infrastructure": [
        (
            "VPC Network Design",
            "The team reviewed VPC CIDR allocation, public and private subnets, route tables, and network segmentation."
        ),
        (
            "EC2 Web Server Deployment",
            "Engineers discussed deploying a web server on Amazon EC2 with Amazon Linux and selecting appropriate instance types."
        ),
        (
            "RDS Database Architecture",
            "The meeting covered PostgreSQL backups, database subnet groups, storage allocation, and availability requirements."
        ),
        (
            "Application Load Balancing",
            "The team reviewed Application Load Balancer target groups, health checks, and traffic distribution."
        ),
        (
            "Terraform Infrastructure Management",
            "Engineers discussed managing VPC and EC2 resources with Terraform plan, apply, and version-controlled configurations."
        ),
        (
            "S3 Storage Strategy",
            "The meeting examined Amazon S3 versioning, storage classes, lifecycle policies, and object retention."
        ),
        (
            "CloudWatch Monitoring",
            "The team reviewed Amazon CloudWatch CPU metrics, alarms, dashboards, and operational monitoring."
        ),
        (
            "EC2 Auto Scaling",
            "Engineers designed EC2 Auto Scaling launch templates, scaling policies, and capacity management."
        ),
        (
            "VPC Peering",
            "The meeting addressed private connectivity between VPCs, routing configurations, and network reachability."
        ),
        (
            "ECS Container Platform",
            "The team discussed Amazon ECS, Docker containers, task definitions, and application deployment strategies."
        ),
    ],
    "AI & Analytics": [
        (
            "Natural Language Processing",
            "The team explored text tokenization, linguistic preprocessing, and extracting meaningful terms from documents."
        ),
        (
            "TF-IDF Document Analysis",
            "Analysts used TF-IDF to vectorize documents and measure the importance of terms across a collection."
        ),
        (
            "UMAP Visualization",
            "The meeting explored reducing high-dimensional document vectors into two dimensions using UMAP."
        ),
        (
            "HDBSCAN Clustering",
            "Data scientists reviewed unsupervised clustering with HDBSCAN and methods for handling noise points."
        ),
        (
            "LLM Document Classification",
            "The team discussed using large language models to classify meeting minutes and improve prompt design."
        ),
        (
            "RAG Document Retrieval",
            "Engineers explored retrieval-augmented generation to find relevant documents and generate grounded answers."
        ),
        (
            "Python Data Analysis",
            "Analysts aggregated datasets using Python and pandas and visualized results using Matplotlib."
        ),
        (
            "AI Model Evaluation",
            "The team evaluated classification models using accuracy, precision, recall, and F1 score."
        ),
        (
            "Embedding-Based Search",
            "Engineers discussed semantic search using text embeddings and cosine similarity."
        ),
        (
            "AI Agent Workflow",
            "The team designed an AI agent workflow involving external tool calls and automated data analysis."
        ),
    ],
    "Security": [
        (
            "IAM Least Privilege",
            "The security team reviewed IAM roles, policies, and least-privilege access control."
        ),
        (
            "KMS Encryption",
            "Engineers discussed encryption key management with AWS KMS and protecting data in transit using TLS."
        ),
        (
            "CloudTrail Auditing",
            "The meeting reviewed AWS CloudTrail API activity logging, audit trails, and event retention."
        ),
        (
            "Vulnerability Management",
            "The team discussed detecting server vulnerabilities and prioritizing remediation activities."
        ),
        (
            "Security Group Rules",
            "Engineers reviewed restricting EC2 inbound access to approved source networks and required ports."
        ),
        (
            "AWS WAF Protection",
            "The security team discussed AWS WAF rules for SQL injection and malicious HTTP request protection."
        ),
        (
            "Multi-Factor Authentication",
            "The meeting covered enforcing multi-factor authentication for administrative accounts."
        ),
        (
            "Incident Response",
            "The team reviewed intrusion detection, initial response, evidence preservation, and recovery procedures."
        ),
        (
            "GuardDuty Threat Detection",
            "Engineers discussed Amazon GuardDuty findings and investigating suspicious API activities."
        ),
        (
            "Secrets Manager",
            "The team reviewed storing database credentials securely using AWS Secrets Manager."
        ),
    ],
}


def connect_db():
    required = [
        "DB_HOST", "DB_PORT", "DB_NAME",
        "DB_USER", "DB_PASSWORD",
        "AWS_PROFILE", "AWS_REGION",
    ]
    missing = [key for key in required if not CONFIG.get(key)]
    if missing:
        raise RuntimeError(
            "Missing environment variables: " + ", ".join(missing)
        )

    return psycopg2.connect(
        host=CONFIG["DB_HOST"],
        port=int(CONFIG["DB_PORT"]),
        dbname=CONFIG["DB_NAME"],
        user=CONFIG["DB_USER"],
        password=CONFIG["DB_PASSWORD"],
        connect_timeout=10,
    )


def get_demo_rows(cur):
    cur.execute(
        """
        SELECT id, title, content, category, ai_category
        FROM meeting_minutes
        WHERE left(title, %s) = %s
        ORDER BY id
        """,
        (len(PREFIX), PREFIX),
    )
    return cur.fetchall()


def seed(conn):
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                ALTER TABLE meeting_minutes
                ADD COLUMN IF NOT EXISTS ai_category VARCHAR(50)
                """
            )

            existing = get_demo_rows(cur)

            if existing:
                if len(existing) != 30:
                    raise RuntimeError(
                        f"Expected 30 existing English records, "
                        f"but found {len(existing)}. No changes made."
                    )
                print("Using 30 existing English demo records.")
                return

            index = 0

            for category, items in DEMO.items():
                for title, content in items:
                    cur.execute(
                        """
                        INSERT INTO meeting_minutes
                        (meeting_date, title, content, category, ai_category)
                        VALUES (%s, %s, %s, %s, NULL)
                        """,
                        (
                            date(2026, 9, 1) + timedelta(days=index),
                            PREFIX + title,
                            content,
                            category,
                        ),
                    )
                    index += 1

            print(f"Inserted {index} synthetic English records.")


def classify_document(bedrock, title, content):
    prompt = f"""
You are classifying synthetic technical meeting minutes.

Choose exactly one category:

Infrastructure
AI & Analytics
Security

Classification guidance:
- Infrastructure: cloud networks, compute, databases,
  storage, deployment, and monitoring.
- AI & Analytics: machine learning, LLMs, data analysis,
  document processing, and AI agents.
- Security: access control, encryption, auditing,
  threat detection, and incident response.

Return only the exact category name.
Do not include explanations.

Title: {title}
Content: {content}
"""

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "temperature": 0.0,
            "maxTokens": 100,
        },
    )

    answer = "".join(
        item.get("text", "")
        for item in response["output"]["message"]["content"]
    ).strip()

    if answer in CATEGORIES:
        return answer

    matches = [category for category in CATEGORIES if category in answer]

    if len(matches) == 1:
        return matches[0]

    raise ValueError(f"Unexpected model response: {answer}")


def run_classification(conn):
    session = boto3.Session(
        profile_name=CONFIG["AWS_PROFILE"],
        region_name=CONFIG["AWS_REGION"],
    )

    bedrock = session.client("bedrock-runtime")

    with conn.cursor() as cur:
        rows = get_demo_rows(cur)

    if len(rows) != 30:
        raise RuntimeError(
            f"Expected 30 English records, found {len(rows)}."
        )

    for doc_id, title, content, actual, predicted in rows:
        if predicted in CATEGORIES:
            print(f"Document {doc_id}: using existing prediction.")
            continue

        prediction = classify_document(bedrock, title, content)

        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE meeting_minutes
                    SET ai_category = %s
                    WHERE id = %s
                    """,
                    (prediction, doc_id),
                )

        print(f"Document {doc_id}: {prediction}")

    print("Amazon Bedrock classification completed.")


def visualize(conn):
    with conn.cursor() as cur:
        rows = get_demo_rows(cur)

    if len(rows) != 30:
        raise RuntimeError("Exactly 30 English records are required.")

    if any(row[4] not in CATEGORIES for row in rows):
        raise RuntimeError(
            "Some documents have not been classified. "
            "Run the classify command first."
        )

    texts = [row[1] + " " + row[2] for row in rows]
    actual = [row[3] for row in rows]
    predicted = [row[4] for row in rows]
    document_ids = [row[0] for row in rows]

    correct = sum(a == p for a, p in zip(actual, predicted))
    incorrect = len(rows) - correct
    accuracy = correct / len(rows) * 100
    counts = Counter(predicted)

    # English documents can use word-based TF-IDF.
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(texts)

    coords = umap.UMAP(
        n_components=2,
        n_neighbors=8,
        min_dist=0.3,
        metric="cosine",
        random_state=42,
    ).fit_transform(matrix)

    colors = {
        "Infrastructure": "#2780C2",
        "AI & Analytics": "#29A354",
        "Security": "#EF8933",
    }

    fig = plt.figure(figsize=(16, 9), facecolor="#101C32")

    fig.text(
        0.055, 0.91,
        "AI-Powered Meeting Minutes Classification",
        fontsize=23,
        color="white",
        fontweight="bold",
    )

    fig.text(
        0.055, 0.85,
        "30 Synthetic English Documents | Amazon Bedrock Nova Micro",
        fontsize=13,
        color="#C7D3E5",
    )

    ax = fig.add_axes([0.07, 0.16, 0.59, 0.61])
    ax.set_facecolor("#172840")

    x, y = coords[:, 0], coords[:, 1]

    # Optional document-density contours.
    try:
        if np.linalg.matrix_rank(np.cov(coords.T)) == 2:
            xx, yy = np.mgrid[
                x.min() - 1:x.max() + 1:120j,
                y.min() - 1:y.max() + 1:120j,
            ]

            kde = gaussian_kde(np.vstack([x, y]))
            density = kde(
                np.vstack([xx.ravel(), yy.ravel()])
            ).reshape(xx.shape)

            ax.contour(
                xx, yy, density,
                levels=8,
                colors="#71839A",
                linewidths=0.6,
                alpha=0.4,
            )
    except (ValueError, np.linalg.LinAlgError):
        pass

    for category in CATEGORIES:
        mask = np.array([p == category for p in predicted])

        ax.scatter(
            x[mask], y[mask],
            s=125,
            color=colors[category],
            edgecolors="white",
            linewidths=0.8,
            label=category,
            zorder=3,
        )

    # Highlight classification errors.
    errors = np.array([
        a != p for a, p in zip(actual, predicted)
    ])

    ax.scatter(
        x[errors], y[errors],
        s=235,
        facecolors="none",
        edgecolors="#FF5964",
        linewidths=2.2,
        label="Incorrect prediction",
        zorder=4,
    )

    for i, doc_id in enumerate(document_ids):
        ax.annotate(
            str(doc_id),
            (x[i], y[i]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            color="white",
        )

    ax.set_title(
        "Document Feature Map (TF-IDF + UMAP)",
        color="white",
        fontsize=15,
    )
    ax.set_xlabel("UMAP Dimension 1", color="white")
    ax.set_ylabel("UMAP Dimension 2", color="white")
    ax.tick_params(colors="white")

    for spine in ax.spines.values():
        spine.set_color("#60738B")

    legend = ax.legend(
        loc="best",
        fontsize=9,
        facecolor="#253750",
        edgecolor="#60738B",
    )

    for text in legend.get_texts():
        text.set_color("white")

    panel = fig.add_axes([0.70, 0.16, 0.27, 0.61])
    panel.set_facecolor("#1B2C46")
    panel.set_xticks([])
    panel.set_yticks([])

    panel.text(
        0.08, 0.88,
        "Classification Results",
        fontsize=18,
        color="white",
        fontweight="bold",
        transform=panel.transAxes,
    )

    panel.text(
        0.08, 0.76,
        f"Documents: {len(rows)}",
        fontsize=13,
        color="white",
        transform=panel.transAxes,
    )

    panel.text(
        0.08, 0.68,
        f"Correct: {correct}",
        fontsize=13,
        color="white",
        transform=panel.transAxes,
    )

    panel.text(
        0.08, 0.60,
        f"Incorrect: {incorrect}",
        fontsize=13,
        color="#FF8991",
        transform=panel.transAxes,
    )

    for i, category in enumerate(CATEGORIES):
        panel.text(
            0.08, 0.45 - i * 0.09,
            f"{category}: {counts[category]}",
            color=colors[category],
            fontsize=11,
            transform=panel.transAxes,
        )

    panel.text(
        0.08, 0.09,
        f"Accuracy: {accuracy:.1f}%",
        fontsize=20,
        color="white",
        fontweight="bold",
        transform=panel.transAxes,
    )

    fig.text(
        0.055, 0.07,
        "Position: TF-IDF + UMAP | Color: Nova Micro Prediction "
        "| Red Ring: Misclassification",
        fontsize=10,
        color="#C7D3E5",
    )

    image_path = OUTPUT / "english_classification_map.png"

    # Save through memory to avoid direct Matplotlib file-open issues.
    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=160,
        facecolor=fig.get_facecolor(),
    )
    image_path.write_bytes(buffer.getvalue())
    plt.close(fig)

    report = (
        "Amazon Bedrock / Amazon Nova Micro\n"
        "Dataset: 30 Synthetic English Meeting Minutes\n"
        f"Documents: {len(rows)}\n"
        f"Correct: {correct}\n"
        f"Incorrect: {incorrect}\n"
        f"Accuracy: {accuracy:.2f}%\n\n"
        "Predicted Categories:\n"
        + "".join(
            f"{category}: {counts[category]}\n"
            for category in CATEGORIES
        )
    )

    report_path = OUTPUT / "english_classification_evaluation.txt"
    report_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"Visualization saved: {image_path}")
    print(f"Evaluation saved: {report_path}")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {
        "seed", "classify", "visualize", "all"
    }:
        print(
            "Usage: python src/demo_bedrock_pipeline.py "
            "seed|classify|visualize|all"
        )
        sys.exit(1)

    conn = connect_db()

    try:
        action = sys.argv[1]

        if action in ("seed", "all"):
            seed(conn)

        if action in ("classify", "all"):
            run_classification(conn)

        if action in ("visualize", "all"):
            visualize(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
