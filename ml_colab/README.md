# Memora — Google Colab ML Integration

This folder prepares the existing project for ML training in Google Colab.

## Workflow
1. Upload this whole project ZIP to Google Colab.
2. Open `ml_colab/01_train_memora_model.ipynb`.
3. Run the notebook from top to bottom.
4. It creates trained model artifacts in `ml_colab/artifacts/`.
5. Copy the generated model artifacts into the Flask backend's `ml_models/` folder.
6. Connect the game's session features to `/api/predict`.

The starter notebook uses synthetic development data only when no approved dataset is supplied.
Do not describe synthetic results as clinical validation or use the model to diagnose dementia.
The intended prototype function is cognitive-performance monitoring and adaptive game difficulty.
