from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
metadata = ROOT / "ml" / "trained_models" / "metadata.json"
if not metadata.exists():
    raise SystemExit("No trained model metadata found. Run ml/training/train.py first.")
data = json.loads(metadata.read_text(encoding="utf-8"))
print("Selected model:", data["model_name"])
print("Test metrics:")
for key, value in data["test_metrics"].items():
    print(f"  {key}: {value:.6f}" if isinstance(value, float) else f"  {key}: {value}")
print("Confusion matrix:", data["confusion_matrix"])
