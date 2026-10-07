# TraceFake Testing

Run:

```bash
python -m pytest tests -q
```

Testing layers:

1. Unit tests
   - URL parsing
   - feature extraction
   - rule scoring
   - classification boundaries

2. API tests
   - health endpoint

3. ML evaluation
   - train/validation/test separation
   - model comparison
   - final test metrics
   - confusion matrix

4. Manual UI tests
   - desktop
   - tablet
   - mobile
   - keyboard navigation
   - invalid URL handling
   - empty database states
