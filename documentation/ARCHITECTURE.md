# TraceFake Architecture

TraceFake is separated into frontend, API, detection, ML, database, reporting, and testing layers.

The production scanner uses static URL analysis. It does not fetch arbitrary destinations.

## Request path

Frontend -> FastAPI -> detector -> feature extractor + ML model + rule engine -> risk engine -> SQLite -> frontend.

## Data path

The model is trained from the same URL-derived feature extractor used at inference time. This reduces train/serve feature mismatch.

## Security boundary

No URL submitted to the scanner is automatically opened. Optional external reputation services should be isolated behind a separate service interface and disabled by default.
