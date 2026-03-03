# Trainr API Specification

## Base URL
```
http://localhost:8000
```

## CORS Configuration
The API accepts requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `*` (all origins)

---

## Endpoints

### GET /health
Health check endpoint to verify backend is running.

**Response:**
```json
{
  "status": "ok"
}
```

---

### POST /upload
Upload and analyze a data file.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): Data file (.csv, .xlsx, .xls, .parquet, .json, .txt)

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "data.csv",
  "shape": {
    "rows": 1000,
    "cols": 15
  },
  "columns": [
    {
      "name": "age",
      "dtype": "int64",
      "null_count": 2,
      "unique_count": 45,
      "sample_values": [25, 30, 35, 40, 45]
    }
  ],
  "preview": [
    {"age": 25, "salary": 50000, "experience": 2},
    {"age": 30, "salary": 60000, "experience": 5}
  ],
  "inferred_types": {
    "age": "numeric",
    "salary": "numeric",
    "name": "text",
    "hired_date": "datetime",
    "department": "categorical"
  },
  "stats": {
    "age": {"mean": 35.5, "std": 10.2, "min": 20, "max": 65},
    "salary": {"mean": 55000, "std": 15000, "min": 30000, "max": 150000}
  }
}
```

**Errors:**
- `400`: Unsupported file format or file parsing error
- `413`: File too large

---

### POST /train
Train a single ML model.

**Request:**
```json
{
  "file_id": "uuid-string",
  "model_type": "xgboost_classifier",
  "target_column": "hired",
  "feature_columns": ["age", "experience", "salary"],
  "date_column": null,
  "params": {
    "n_estimators": 100,
    "max_depth": 5,
    "learning_rate": 0.1
  },
  "test_size": 0.2,
  "cv_folds": 5
}
```

**Response (Classification Example):**
```json
{
  "model_type": "xgboost_classifier",
  "task_type": "classification",
  "training_time_seconds": 2.45,
  "metrics": {
    "accuracy": 0.92,
    "precision": 0.89,
    "recall": 0.91,
    "f1": 0.90,
    "roc_auc": 0.95
  },
  "y_test": [1, 0, 1, 1, 0],
  "y_pred": [1, 0, 1, 1, 0],
  "y_prob": [0.95, 0.12, 0.88, 0.91, 0.08],
  "confusion_matrix": [[45, 5], [3, 47]],
  "feature_importances": {
    "experience": 0.45,
    "salary": 0.35,
    "age": 0.20
  }
}
```

**Response (Regression Example):**
```json
{
  "model_type": "xgboost_regressor",
  "task_type": "regression",
  "training_time_seconds": 1.82,
  "metrics": {
    "mae": 2500,
    "mse": 8900000,
    "rmse": 2983,
    "mape": 0.045,
    "r2": 0.87
  },
  "y_test": [50000, 60000, 55000, 70000],
  "y_pred": [51000, 59500, 54800, 71200],
  "residuals": [1000, -500, -200, 1200],
  "feature_importances": {
    "experience": 0.52,
    "age": 0.30,
    "education_level": 0.18
  }
}
```

**Response (Time Series Example):**
```json
{
  "model_type": "arima",
  "task_type": "time_series",
  "training_time_seconds": 3.12,
  "metrics": {
    "mae": 1.5,
    "mse": 3.2,
    "rmse": 1.79,
    "mape": 0.08
  },
  "actual": [100, 105, 110, 115, 120],
  "forecast": [101, 106, 111, 116, 121],
  "dates": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
  "confidence_lower": [98, 103, 108, 113, 118],
  "confidence_upper": [104, 109, 114, 119, 124]
}
```

**Response (Clustering Example):**
```json
{
  "model_type": "kmeans",
  "task_type": "clustering",
  "training_time_seconds": 0.95,
  "metrics": {
    "silhouette_score": 0.72,
    "inertia": 1250.5
  },
  "labels": [0, 1, 0, 2, 1, 0],
  "pca_2d": [[1.2, 3.4], [5.6, 2.1], [1.3, 3.5], [8.9, 1.2], [5.5, 2.2], [1.1, 3.6]]
}
```

**Response (Deep Learning Example):**
```json
{
  "model_type": "lstm",
  "task_type": "regression",
  "training_time_seconds": 15.3,
  "metrics": {
    "mae": 2.1,
    "mse": 6.8,
    "rmse": 2.6,
    "mape": 0.042,
    "r2": 0.92
  },
  "y_test": [100, 105, 110],
  "y_pred": [101, 104.5, 111],
  "training_history": {
    "epoch": [0, 1, 2, 3, 4],
    "loss": [5.2, 4.8, 4.1, 3.8, 3.5],
    "val_loss": [5.5, 5.0, 4.5, 4.2, 3.9],
    "accuracy": [0.75, 0.78, 0.82, 0.85, 0.87]
  }
}
```

**Errors:**
- `400`: Missing required fields, invalid model type, or training error
- `404`: File ID not found (expired session)

---

### POST /compare
Train and compare up to 3 models.

**Request:**
```json
[
  {
    "file_id": "uuid-string",
    "model_type": "xgboost_classifier",
    "target_column": "hired",
    "feature_columns": ["age", "experience"],
    "params": {"n_estimators": 100},
    "test_size": 0.2
  },
  {
    "file_id": "uuid-string",
    "model_type": "random_forest_classifier",
    "target_column": "hired",
    "feature_columns": ["age", "experience"],
    "params": {"n_estimators": 100},
    "test_size": 0.2
  }
]
```

**Response:**
```json
{
  "models": [
    { /* full training response for model 1 */ },
    { /* full training response for model 2 */ }
  ]
}
```

**Errors:**
- `400`: More than 3 models, invalid parameters, or training errors
- `404`: File ID not found

---

## Error Response Format

All errors return `Content-Type: application/json` with HTTP status code 4xx or 5xx:

```json
{
  "error": "Descriptive error message"
}
```

Examples:
```json
{"error": "File format not supported. Accepted formats: csv, xlsx, parquet, json, txt"}
{"error": "Model type 'invalid_model' not found"}
{"error": "Target column 'missing_col' not found in data"}
{"error": "TensorFlow not installed. Install with: pip install tensorflow"}
```

---

## Session Management

- Files are stored server-side in an in-memory dictionary
- Each file gets a unique UUID (`file_id`)
- Session data persists until the server restarts
- For production, implement persistent storage (database)

---

## Model Types

### Regression
- `linear_regression`
- `ridge`
- `lasso`
- `random_forest_regressor`
- `xgboost_regressor`
- `gradient_boosting_regressor`
- `svr`

### Classification
- `logistic_regression`
- `random_forest_classifier`
- `xgboost_classifier`
- `svm_classifier`
- `knn`
- `naive_bayes`
- `gradient_boosting_classifier`

### Time Series
- `arima`
- `sarima`
- `exponential_smoothing`

### Clustering
- `kmeans`
- `dbscan`
- `hierarchical`

### Deep Learning (TensorFlow)
- `mlp`
- `lstm`
- `cnn_1d`
- `autoencoder`

---

## Rate Limiting & Timeouts

- No built-in rate limiting (consider adding for production)
- Request timeout: 5 minutes (configurable in `uvicorn`)
- File upload size limit: 100MB (configurable)

---

## Testing

Example using curl:

```bash
# Health check
curl http://localhost:8000/health

# Upload file
curl -X POST -F "file=@data.csv" http://localhost:8000/upload

# Train model
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "...",
    "model_type": "xgboost_classifier",
    "target_column": "target",
    "feature_columns": ["feat1", "feat2"],
    "params": {},
    "test_size": 0.2
  }'
```
