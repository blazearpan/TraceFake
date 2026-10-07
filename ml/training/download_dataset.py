from pathlib import Path
import ssl
import urllib.request
import urllib.error
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ml" / "datasets"
OUT.mkdir(parents=True, exist_ok=True)

URL = "https://archive.ics.uci.edu/static/public/967/phiusiil%2Bphishing%2Burl%2Bdataset.zip"
ZIP_PATH = OUT / "phiusiil_dataset.zip"
CSV_PATH = OUT / "PhiUSIIL_Phishing_URL_Dataset.csv"

print("Downloading UCI PhiUSIIL Phishing URL Dataset...")

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "TraceFake/1.0 Dataset Downloader"
    }
)

try:
    # First attempt: normal SSL verification.
    with urllib.request.urlopen(request, timeout=60) as response:
        ZIP_PATH.write_bytes(response.read())

except (urllib.error.URLError, ssl.SSLError) as error:
    print()
    print("Normal SSL download failed.")
    print(f"Reason: {error}")
    print()
    print("Retrying the UCI dataset download...")

    # This exception is limited to this specific public dataset download.
    insecure_context = ssl._create_unverified_context()

    with urllib.request.urlopen(
        request,
        context=insecure_context,
        timeout=60
    ) as response:
        ZIP_PATH.write_bytes(response.read())

print(f"Downloaded: {ZIP_PATH}")
print(f"File size: {ZIP_PATH.stat().st_size / (1024 * 1024):.2f} MB")

if ZIP_PATH.stat().st_size < 1_000_000:
    raise RuntimeError(
        "The downloaded file is unexpectedly small. "
        "The UCI dataset download may have failed."
    )

print("Reading dataset ZIP...")

with zipfile.ZipFile(ZIP_PATH, "r") as archive:

    csv_files = [
        name for name in archive.namelist()
        if name.lower().endswith(".csv")
    ]

    if not csv_files:
        raise RuntimeError(
            "No CSV file was found inside the UCI dataset ZIP."
        )

    print("CSV file found:")
    for name in csv_files:
        print(f"  {name}")

    selected_csv = csv_files[0]

    with archive.open(selected_csv) as source:
        frame = pd.read_csv(source)

print(f"Rows: {len(frame)}")
print(f"Columns: {len(frame.columns)}")

# The official UCI dataset uses "Label".
label_candidates = [
    column
    for column in frame.columns
    if str(column).strip().lower() == "label"
]

if not label_candidates:
    raise RuntimeError(
        "Could not find the official 'Label' column.\n"
        f"Available columns: {list(frame.columns)}"
    )

label_column = label_candidates[0]

if label_column != "Label":
    frame = frame.rename(columns={label_column: "Label"})

frame.to_csv(CSV_PATH, index=False)

print()
print("Dataset download completed successfully.")
print(f"Saved: {CSV_PATH}")
print(f"Rows: {len(frame)}")
print(f"Columns: {len(frame.columns)}")
print()
print("Official UCI label meaning:")
print("1 = legitimate URL")
print("0 = phishing URL")