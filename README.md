# AWS Meeting Minutes Analytics & AI-Powered Classification

**AWS × Amazon Bedrock × PostgreSQL × Python**

An end-to-end cloud and generative AI engineering portfolio project that automatically classifies Japanese meeting minutes stored in Amazon RDS for PostgreSQL using **Amazon Bedrock (Amazon Nova Micro)** and visualizes document relationships using **TF-IDF and UMAP**.

**English edition and measurement provenance:** The published results are English translations/presentations of measurements made on the original Japanese dataset. Document IDs, predictions, counts, accuracy, UMAP coordinates, and clustering scores have not been recalculated. The included Python script is a separate English-language demo; its results must be measured independently. See [the English-edition audit](docs/english-edition-audit.md).

## 1. Project Overview

This project demonstrates the integration of AWS cloud infrastructure, private database connectivity, generative AI, Python automation, data visualization, and classification evaluation.

The demonstration uses **30 synthetic Japanese meeting minutes**. No real customer data or confidential business information is included.

### Key Features

- Meeting minutes storage in Amazon RDS for PostgreSQL
- Secure private database access through AWS Systems Manager
- Automated document classification using Amazon Bedrock
- Amazon Nova Micro inference through the Converse API
- Python integration using boto3 and psycopg2
- Persistence of AI predictions in PostgreSQL
- Japanese text feature extraction using TF-IDF
- Two-dimensional visualization using UMAP and Matplotlib
- Classification accuracy evaluation

## 2. System Architecture

```text
Windows 11 / Visual Studio Code
              |
              | AWS CLI
              | SSM Port Forwarding
              v
          Amazon EC2
      (SSM-managed instance)
              |
              v
    Amazon RDS PostgreSQL
       meeting_minutes
              ^
              |
       Python / psycopg2
              |
              v
    Retrieve 30 documents
              |
              v
        Amazon Bedrock
        Amazon Nova Micro
              |
              v
    Predict 3 categories
              |
              v
    Store predictions in
     RDS (ai_category)
              |
              v
        TF-IDF + UMAP
              |
              v
    Classification Map
              |
              v
    Accuracy Evaluation
```

The development and Python execution environment runs locally on Windows 11 using Visual Studio Code.

Amazon EC2 provides a secure connection path to the private RDS database through AWS Systems Manager.

The Python application invokes Amazon Bedrock directly using boto3.

## 3. Technology Stack

| Area | Technology | Purpose |
|---|---|---|
| Cloud | AWS | Infrastructure platform |
| Compute | Amazon EC2 | SSM connection intermediary |
| Database | Amazon RDS for PostgreSQL | Document and prediction storage |
| Generative AI | Amazon Bedrock | Managed model inference |
| Foundation Model | Amazon Nova Micro | Document classification |
| Security | AWS IAM | Access control |
| Operations | AWS Systems Manager | Secure database connectivity |
| Programming | Python | Data processing and automation |
| AWS SDK | boto3 | Bedrock API integration |
| Database Driver | psycopg2 | PostgreSQL operations |
| Japanese NLP (original experiment) | SudachiPy | Tokenization of the measured Japanese dataset |
| Feature Extraction | TF-IDF | Text vectorization |
| Dimensionality Reduction | UMAP | Two-dimensional document mapping |
| Visualization | Matplotlib / SciPy | Classification visualization |

## 4. AI-Powered Document Classification

### Dataset

The project uses 30 synthetic Japanese meeting minutes stored in the PostgreSQL `meeting_minutes` table.

### Classification Categories

| Category | Example Topics |
|---|---|
| AWS / Infrastructure | VPC, EC2, RDS, Terraform, S3, CloudWatch |
| AI / Analytics | LLM, RAG, Python, TF-IDF, UMAP, Embeddings |
| Security | IAM, KMS, CloudTrail, WAF, GuardDuty |

### Processing Workflow

1. Retrieve document titles and content from PostgreSQL.
2. Invoke Amazon Nova Micro through the Amazon Bedrock Converse API.
3. Predict one of three predefined categories.
4. Store the prediction in the `ai_category` database column.
5. Compare predictions against predefined ground-truth labels.
6. Calculate classification accuracy.
7. Visualize document relationships using TF-IDF and UMAP.

Ground-truth labels are used for evaluation and are not provided to the model as part of the classification prompt.

## 5. Evaluation Results

Amazon Nova Micro classified all 30 synthetic Japanese meeting minutes in the original measured experiment. The following results are translated for this English edition; they are not results from running the English demo.

### Classification Accuracy

| Metric | Result |
|---|---:|
| Documents evaluated | 30 |
| Model | Amazon Nova Micro |
| Categories | 3 |
| Correct predictions | 24 |
| Incorrect predictions | 6 |
| **Accuracy** | **80.0%** |

### Predicted Category Distribution

| Predicted Category | Documents |
|---|---:|
| AWS / Infrastructure | 4 |
| AI / Analytics | 10 |
| Security | 16 |
| **Total** | **30** |

The model correctly classified 24 out of 30 documents.

The predictions showed an uneven category distribution, with more documents assigned to the Security category.

These results are based on a small synthetic dataset and should not be interpreted as production-level performance.

## 6. Classification Visualization

The project uses TF-IDF and UMAP to map Japanese meeting minutes into a two-dimensional space.

![Amazon Bedrock Meeting Minutes Classification Map](output/bedrock_classification_map.png)

### How to Interpret the Visualization

- **Each point:** One meeting document
- **Point position:** Document features represented through TF-IDF and UMAP
- **Point color:** Category predicted by Amazon Nova Micro
- **Numeric label:** Meeting minutes ID
- **Red outline:** Incorrect classification compared with the ground-truth category

Amazon Nova Micro performs the actual classification.

TF-IDF and UMAP are used for feature representation and visualization, not for determining the predicted category.

The published map presents the original Japanese-document experiment in English. Its saved coordinates and predictions are reused; translating labels does not produce a new model evaluation. The UMAP axes have no inherent semantic meaning.

Additional historical reports are available in [analysis_result.txt](output/analysis_result.txt) and [bedrock_clustering_evaluation.txt](output/bedrock_clustering_evaluation.txt). The TF-IDF/UMAP/HDBSCAN report records ARI 0.4493 and NMI 0.6184. The separate Bedrock clustering experiment records ARI 1.0000, NMI 1.0000, and agreement 30/30 (100.00%). These are separate clustering experiments and must not be confused with the classification accuracy above.

## 7. Development Environment

- Operating system: Windows 11
- IDE: Visual Studio Code
- Terminal: PowerShell
- Programming language: Python
- AWS Region: Asia Pacific (Tokyo), `ap-northeast-1`
- Database: Amazon RDS for PostgreSQL
- Generative AI: Amazon Bedrock / Amazon Nova Micro

## 8. Getting Started

This workflow creates and processes **30 synthetic English documents**, using titles prefixed with `[EN-DEMO2026] `. It is a separate experiment from the saved Japanese-data results above. The script selects only these prefixed records and saves new English-demo outputs under different filenames.

The database must already contain a `meeting_minutes` table with an automatically generated `id` and the columns `meeting_date`, `title`, `content`, and `category`. The seed command adds `ai_category` if needed. AWS credentials, Bedrock model access, and an SSM connection to the private database are required. Running classification invokes Amazon Bedrock and can incur AWS charges.

### 8.1 Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 8.2 Configure Environment Variables

Create a `.env.local` file in the project root.

```dotenv
DB_HOST=127.0.0.1
DB_PORT=15432
DB_NAME=minutesdb
DB_USER=YOUR_DB_USER
DB_PASSWORD=YOUR_DB_PASSWORD
AWS_PROFILE=YOUR_AWS_PROFILE
AWS_REGION=ap-northeast-1
```

Do not commit credentials or local environment files to GitHub.

### 8.3 Establish an SSM Port Forwarding Session

Use a managed EC2 instance with network access to the private RDS endpoint.

```powershell
aws ssm start-session `
  --target YOUR_EC2_INSTANCE_ID `
  --document-name AWS-StartPortForwardingSessionToRemoteHost `
  --parameters '{"host":["YOUR_RDS_ENDPOINT"],"portNumber":["5432"],"localPortNumber":["15432"]}' `
  --region ap-northeast-1 `
  --profile YOUR_AWS_PROFILE
```

Keep this session running and open another PowerShell terminal to execute the Python commands.

### 8.4 Seed the Demonstration Dataset

```powershell
python .\src\demo_bedrock_pipeline.py seed
```

### 8.5 Classify Documents with Amazon Bedrock

```powershell
python .\src\demo_bedrock_pipeline.py classify
```

### 8.6 Run the Visualization Workflow

```powershell
python .\src\demo_bedrock_pipeline.py visualize
```

### 8.7 View the Newly Generated English-Demo Map

```powershell
Start-Process .\output\english_classification_map.png
```

The visualization command also writes `output/english_classification_evaluation.txt`. These files contain new measurements for the English demo. No English-demo accuracy is claimed until that workflow has been run and evaluated.

The published `output/bedrock_classification_map.png` is the historical Japanese-data map with English presentation. The English-demo command does not reproduce that experiment or overwrite that file.

## 9. Repository Structure

```text
aws-bedrock-minutes-analytics/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── docs/
│   └── english-edition-audit.md
├── src/
│   └── demo_bedrock_pipeline.py
└── output/
    ├── analysis_result.txt
    ├── bedrock_classification_map.png
    ├── bedrock_classification_result.txt
    └── bedrock_clustering_evaluation.txt
```

### Main Demonstration Script

`src/demo_bedrock_pipeline.py`

The script provides English-demo commands for dataset creation, Bedrock classification, and visualization. Its comments, prompts, synthetic documents, console messages, and generated report labels are in English.

The committed text reports are translations of historical Japanese-data experiments. The original Japanese analysis and clustering scripts are available in the [Japanese repository](https://github.com/mika-it-labs/minutes-analytics); they are not included in this English edition. Image paths printed inside the historical analysis log record files saved during that original run; those additional images are not included here.

New demo runs additionally generate `output/english_classification_map.png` and `output/english_classification_evaluation.txt`.

## 10. Security Considerations

- PostgreSQL is deployed in a private network.
- Database connectivity is established through AWS Systems Manager.
- EC2 administration does not require publicly exposing SSH.
- AWS IAM controls access to AWS services.
- Database credentials are excluded from version control.
- Only synthetic meeting minutes are used for testing.

## 11. Engineering Skills Demonstrated

### AWS Cloud Engineering

- EC2 and RDS integration
- Private database connectivity
- IAM permissions and troubleshooting
- AWS Systems Manager port forwarding

### Generative AI and Data Engineering

- Amazon Bedrock Converse API integration
- Python automation using boto3
- Japanese document classification
- PostgreSQL data persistence
- TF-IDF text feature extraction
- UMAP dimensionality reduction
- Matplotlib data visualization
- Classification accuracy evaluation

### Development and Operations

- Windows 11 and Visual Studio Code development
- Python virtual environments
- AWS CLI operations
- Git and GitHub version control
- Debugging and technical documentation

## 12. Future Improvements

- Investigate the six misclassified documents
- Improve classification prompts
- Evaluate Precision, Recall, and F1-score
- Expand the evaluation dataset
- Add automated Python tests
- Introduce CI/CD workflows

---

**Project Type:** Independent cloud and generative AI engineering portfolio

**AWS Region:** Asia Pacific (Tokyo), `ap-northeast-1`

**Dataset:** 30 synthetic Japanese meeting minutes

**Classification Accuracy:** 80.0%

**Japanese Version:** https://github.com/mika-it-labs/minutes-analytics
