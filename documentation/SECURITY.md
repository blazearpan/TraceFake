# TraceFake Security Model

## Safe static analysis

The default analyzer:
- parses the URL
- extracts features
- evaluates rules
- runs the local ML model
- writes scan metadata to SQLite

It does not:
- browse to the submitted URL
- execute remote JavaScript
- download files
- submit credentials
- exploit targets
- run arbitrary commands

## Stored data

SQLite stores the submitted URL, timestamp, classification, risk scores, model information, feature values, and detection reasons.

No password, cookie, authentication token, or submitted credential is intentionally collected.

## Risk communication

A SAFE classification is not a guarantee of safety.

A PHISHING classification is a risk assessment and should be independently verified.

The risk score is not a calibrated probability.
