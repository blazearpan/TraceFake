# TraceFake ML Methodology

## Dataset

Primary dataset: PhiUSIIL Phishing URL (Website), UCI Machine Learning Repository.

The original dataset contains 235,795 instances and 54 features. TraceFake intentionally uses only the URL column and label for its own URL-only feature pipeline.

## Label mapping

UCI label:
- 1 = legitimate
- 0 = phishing

TraceFake target:
- 0 = legitimate
- 1 = phishing

## Preprocessing

- Remove missing URLs.
- Strip whitespace.
- Remove exact duplicate URLs.
- Extract URL-only features with the same module used in live scanning.

## Split

A stratified 70/15/15 train/validation/test split is used with random seed 42.

## Model selection

Candidates:
- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting

The selected model is the model with the strongest validation F1 score. Validation ROC-AUC is used as the tie-breaker. The final test set remains untouched until final evaluation.

## Metrics

Accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrix are reported.

No metric is predetermined or hardcoded.

## Limitation

The UCI dataset includes additional webpage/source-derived features that TraceFake does not use because the production scanner is designed not to open submitted URLs. Therefore, TraceFake's reported results are for its URL-only feature representation and must not be presented as the performance of the full original 54-feature dataset.
