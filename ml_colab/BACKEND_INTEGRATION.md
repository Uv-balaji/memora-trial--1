# Backend integration after Colab training

After running the notebook, copy:
- ml_colab/artifacts/memora_model.joblib
- ml_colab/artifacts/feature_schema.json

to:
ml_models/
  memora_model.joblib
  feature_schema.json

Then update Flask `/api/predict` to:
1. Validate feature names.
2. Build a one-row DataFrame in the exact training order.
3. Load the joblib pipeline.
4. Return prediction + probability.
5. Use the output for adaptive difficulty and caregiver insights.

Do not present the output as a medical diagnosis.
