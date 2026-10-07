# TRACEFAKE

## Trace the Link. Detect the Threat.

TraceFake is a local-first phishing URL detection and risk analysis system combining:

- URL-only feature engineering
- Machine learning
- Security heuristics
- Configurable risk scoring
- Explainable detection
- SQLite scan history
- Analytics from real scans
- Model performance reporting
- PDF security reports
- Optional reputation integration point

The project is designed for a final-year cybersecurity / machine-learning project. It does **not** claim 100% detection accuracy and does not automatically open submitted URLs.

## Important: ML model setup

The application intentionally does not ship with a fabricated trained model.

Before expecting ML-based results, download/train a model from the real UCI PhiUSIIL Phishing URL Dataset:

https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset

The dataset contains URL records and labels. TraceFake uses only the URL column plus the dataset label for its URL-only training pipeline. This keeps the deployed scanner consistent with the safe static-analysis design.

Dataset citation:

Prasad, A. & Chandra, S. (2024). PhiUSIIL Phishing URL (Website). UCI Machine Learning Repository.
DOI: https://doi.org/10.1016/j.cose.2023.103545
License: CC BY 4.0

## Requirements

- Windows 10/11, Linux, or macOS
- Python 3.11+ (Python 3.13 is supported by the dependency ranges when compatible wheels are available)
- Node.js 20+
- npm
- Internet is required only to download the dataset/dependencies. Scanning itself is local.

## Quick start - Windows

1. Open a terminal inside `TraceFake`.
2. Run:

```bat
setup_windows.bat
```

3. Download the dataset:

```bat
venv\Scripts\python.exe ml\training\download_dataset.py
```

4. Train and evaluate:

```bat
venv\Scripts\python.exe ml\training\train.py
```

5. Start the application:

```bat
run_windows.bat
```

Frontend: http://localhost:5173
Backend: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

## Manual setup

### Backend

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

### Frontend

```bat
cd frontend
npm install
cd ..
```

### Dataset

```bat
venv\Scripts\python.exe ml\training\download_dataset.py
```

### Training

```bat
venv\Scripts\python.exe ml\training\train.py
```

### Run backend

```bat
venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Run frontend

In another terminal:

```bat
cd frontend
npm run dev
```

## Project behavior

TraceFake performs static URL analysis. It does not fetch the destination by default.

Pipeline:

```text
URL
 -> safe parsing
 -> URL feature extraction
 -> ML prediction
 -> security rules
 -> optional reputation status
 -> configurable hybrid risk score
 -> classification
 -> explanation
```

Default classification thresholds are configurable in `backend/app/core/config.py`:

- 0-29: SAFE
- 30-69: SUSPICIOUS
- 70-100: PHISHING

These are project thresholds, not universal industry standards.

## ML methodology

The training pipeline:

1. Loads the legitimate public dataset.
2. Validates required columns.
3. Removes exact duplicate URLs.
4. Extracts the same URL-only features used by the live scanner.
5. Converts UCI labels so phishing = 1 and legitimate = 0.
6. Performs a stratified train/validation/test split.
7. Trains Logistic Regression, Decision Tree, Random Forest, and Gradient Boosting.
8. Selects a model using validation F1, with validation ROC-AUC as the tie-breaker.
9. Evaluates the selected model once on the untouched test set.
10. Saves the selected model, feature schema, metrics, and comparison data.

No performance number is written into the project until the training command actually produces it.

## Why URL-only training?

The UCI dataset contains URL fields as well as additional webpage/source-derived features. The deployed TraceFake scanner intentionally does not open arbitrary URLs. Training only on URL-derived features makes the model's input contract match the production scanner and avoids pretending that source-code features are available during safe static scanning.

This means the resulting performance is specifically the performance of the URL-only feature representation, not the performance of every feature published in the original dataset.

## Security notes

TraceFake does not:

- automatically browse submitted URLs
- execute downloaded files
- submit credentials
- exploit websites
- run shell commands derived from URLs
- store passwords, cookies, or authentication tokens

Treat results as risk assessment, not proof that a site is safe or malicious.

## Tests

Run:

```bat
venv\Scripts\python.exe -m pytest tests -q
```

The tests cover URL parsing, feature extraction, rule scoring, classification boundaries, and API health.

## Structure

```text
TraceFake/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
├── ml/
│   ├── datasets/
│   ├── feature_extraction/
│   ├── evaluation/
│   ├── training/
│   └── trained_models/
├── reports/
├── documentation/
├── tests/
├── setup_windows.bat
└── run_windows.bat
```

## Academic integrity

Do not copy fabricated accuracy into a report. Record the exact dataset version/date, preprocessing choices, random seed, model configuration, test metrics, confusion matrix, and limitations produced by your actual run.

## Ethical use

TraceFake is intended for defensive security education, research, and authorized analysis. It should not be used to facilitate unauthorized access, credential theft, exploitation, or malicious scanning.
