"""
HappyModel Backend - FastAPI Server
A no-code machine learning modeling tool
"""

import io
import uuid
import json
import traceback
from typing import Optional, List, Dict, Any
from pathlib import Path

import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split, cross_val_score, KFold, learning_curve as sk_learning_curve
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, mean_absolute_percentage_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, silhouette_score
)
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans, DBSCAN
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Sequential, Model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# ============================================================================
# FastAPI Setup
# ============================================================================

app = FastAPI(title="HappyModel", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage (in-memory)
SESSIONS: Dict[str, pd.DataFrame] = {}

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}

# ============================================================================
# File Upload & Data Profiling
# ============================================================================

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Upload and profile a data file
    Supported formats: CSV, Excel, Parquet, JSON, TXT
    """
    try:
        # Read file into bytes
        contents = await file.read()

        # Parse based on file extension
        ext = Path(file.filename).suffix.lower()

        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(contents))
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(io.BytesIO(contents))
        elif ext == ".parquet":
            df = pd.read_parquet(io.BytesIO(contents))
        elif ext == ".json":
            df = pd.read_json(io.BytesIO(contents))
        elif ext == ".txt":
            df = pd.read_csv(io.BytesIO(contents), sep="\t")
        else:
            raise ValueError(f"Unsupported format: {ext}")

        # Generate file ID and store
        file_id = str(uuid.uuid4())
        SESSIONS[file_id] = df

        # Profile data
        rows, cols = df.shape

        # Column information
        columns = []
        for col in df.columns:
            columns.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(5).tolist()
            })

        # Infer column types
        inferred_types = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                inferred_types[col] = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                inferred_types[col] = "datetime"
            elif df[col].nunique() / len(df) < 0.05:
                inferred_types[col] = "categorical"
            else:
                inferred_types[col] = "text"

        # Basic statistics for numeric columns
        stats = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            stats[col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "25%": float(df[col].quantile(0.25)),
                "50%": float(df[col].quantile(0.50)),
                "75%": float(df[col].quantile(0.75))
            }

        # Preview (first 10 rows)
        preview = df.head(10).to_dict(orient="records")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "shape": {"rows": rows, "cols": cols},
            "columns": columns,
            "preview": preview,
            "inferred_types": inferred_types,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"File upload error: {str(e)}"
        )

# ============================================================================
# Model Training
# ============================================================================

def get_model(model_type: str, params: Dict[str, Any], task_type: str):
    """Get model instance based on type and parameters"""

    # Regression Models
    if model_type == "linear_regression":
        return LinearRegression()
    elif model_type == "ridge":
        return Ridge(alpha=params.get("alpha", 1.0))
    elif model_type == "lasso":
        return Lasso(alpha=params.get("alpha", 1.0))
    elif model_type == "random_forest_regressor":
        return RandomForestRegressor(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", None),
            min_samples_split=params.get("min_samples_split", 2),
            random_state=42
        )
    elif model_type == "xgboost_regressor":
        if not XGBOOST_AVAILABLE:
            raise ValueError("XGBoost not installed. Install with: pip install xgboost")
        return xgb.XGBRegressor(
            learning_rate=params.get("learning_rate", 0.1),
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 5),
            subsample=params.get("subsample", 1.0),
            colsample_bytree=params.get("colsample_bytree", 1.0),
            random_state=42
        )
    elif model_type == "gradient_boosting_regressor":
        return GradientBoostingRegressor(
            learning_rate=params.get("learning_rate", 0.1),
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 3),
            random_state=42
        )
    elif model_type == "svr":
        return SVR(
            C=params.get("C", 1.0),
            kernel=params.get("kernel", "rbf"),
            gamma=params.get("gamma", "scale")
        )

    # Classification Models
    elif model_type == "logistic_regression":
        return LogisticRegression(
            C=params.get("C", 1.0),
            max_iter=params.get("max_iter", 1000),
            solver=params.get("solver", "lbfgs")
        )
    elif model_type == "random_forest_classifier":
        return RandomForestClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", None),
            min_samples_split=params.get("min_samples_split", 2),
            random_state=42
        )
    elif model_type == "xgboost_classifier":
        if not XGBOOST_AVAILABLE:
            raise ValueError("XGBoost not installed. Install with: pip install xgboost")
        return xgb.XGBClassifier(
            learning_rate=params.get("learning_rate", 0.1),
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 5),
            subsample=params.get("subsample", 1.0),
            colsample_bytree=params.get("colsample_bytree", 1.0),
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    elif model_type == "svm_classifier":
        return SVC(
            C=params.get("C", 1.0),
            kernel=params.get("kernel", "rbf"),
            gamma=params.get("gamma", "scale"),
            probability=True
        )
    elif model_type == "knn":
        return KNeighborsClassifier(n_neighbors=params.get("n_neighbors", 5))
    elif model_type == "naive_bayes":
        return GaussianNB()
    elif model_type == "gradient_boosting_classifier":
        return GradientBoostingClassifier(
            learning_rate=params.get("learning_rate", 0.1),
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 3),
            random_state=42
        )

    # Clustering Models
    elif model_type == "kmeans":
        return KMeans(
            n_clusters=params.get("n_clusters", 3),
            init=params.get("init", "k-means++"),
            max_iter=params.get("max_iter", 300),
            random_state=42
        )
    elif model_type == "dbscan":
        return DBSCAN(
            eps=params.get("eps", 0.5),
            min_samples=params.get("min_samples", 5)
        )
    elif model_type == "hierarchical":
        return AgglomerativeClustering(
            n_clusters=params.get("n_clusters", 3),
            linkage=params.get("linkage", "ward")
        )

    else:
        raise ValueError(f"Unknown model type: {model_type}")

def preprocess_data(df: pd.DataFrame, feature_cols: List[str], target_col: Optional[str] = None):
    """Preprocess data: handle nulls, encode categoricals, etc."""
    df = df.copy()

    # Handle missing values
    for col in feature_cols:
        if df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else "unknown", inplace=True)

    # Handle target column nulls
    if target_col and df[target_col].isnull().sum() > 0:
        if pd.api.types.is_numeric_dtype(df[target_col]):
            df[target_col].fillna(df[target_col].median(), inplace=True)
        else:
            df[target_col].fillna(df[target_col].mode()[0] if len(df[target_col].mode()) > 0 else "unknown", inplace=True)

    # Encode categorical features
    encoders = {}
    for col in feature_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    # Encode target if categorical
    target_encoder = None
    if target_col and not pd.api.types.is_numeric_dtype(df[target_col]):
        target_encoder = LabelEncoder()
        df[target_col] = target_encoder.fit_transform(df[target_col].astype(str))

    return df, encoders, target_encoder

@app.post("/train")
async def train(request_body: Dict[str, Any]):
    """
    Train a single ML model
    """
    try:
        file_id = request_body.get("file_id")
        model_type = request_body.get("model_type")
        target_column = request_body.get("target_column")
        feature_columns = request_body.get("feature_columns", [])
        params = request_body.get("params", {})
        test_size = request_body.get("test_size", 0.2)
        cv_folds = request_body.get("cv_folds", None)

        # Validate
        if file_id not in SESSIONS:
            raise ValueError("File ID not found or session expired")

        df = SESSIONS[file_id]

        # Determine task type based on model
        task_type = "regression"
        if "classifier" in model_type or model_type in ["svm_classifier", "knn", "naive_bayes"]:
            task_type = "classification"
        elif model_type in ["kmeans", "dbscan", "hierarchical"]:
            task_type = "clustering"
        elif model_type in ["arima", "sarima", "exponential_smoothing"]:
            task_type = "time_series"

        # For clustering, we don't need target
        if task_type != "clustering":
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found")

        # Check feature columns
        for col in feature_columns:
            if col not in df.columns:
                raise ValueError(f"Feature column '{col}' not found")

        # Preprocess
        df_processed, encoders, target_encoder = preprocess_data(df, feature_columns, target_column if task_type != "clustering" else None)

        # Prepare data
        X = df_processed[feature_columns].values

        import time
        start_time = time.time()

        if task_type == "clustering":
            # Clustering doesn't need train/test split
            model = get_model(model_type, params, task_type)
            labels = model.fit_predict(X)
            training_time = time.time() - start_time

            # PCA for 2D visualization
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)
            pca_2d = X_pca.tolist()

            # Calculate metrics
            silhouette = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else 0

            inertia = None
            if model_type == "kmeans":
                inertia = float(model.inertia_)

            return {
                "model_type": model_type,
                "task_type": "clustering",
                "training_time_seconds": training_time,
                "metrics": {
                    "silhouette_score": float(silhouette),
                    "inertia": inertia
                },
                "labels": labels.tolist(),
                "pca_2d": pca_2d
            }

        else:
            y = df_processed[target_column].values

            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Get and train model
            model = get_model(model_type, params, task_type)
            model.fit(X_train, y_train)
            training_time = time.time() - start_time

            # Predictions
            y_pred = model.predict(X_test)

            if task_type == "regression":
                # Regression metrics
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                mape = mean_absolute_percentage_error(y_test, y_pred) if np.all(y_test != 0) else 0
                r2 = r2_score(y_test, y_pred)
                residuals = (y_test - y_pred).tolist()

                result = {
                    "model_type": model_type,
                    "task_type": "regression",
                    "training_time_seconds": training_time,
                    "metrics": {
                        "mae": float(mae),
                        "mse": float(mse),
                        "rmse": float(rmse),
                        "mape": float(mape),
                        "r2": float(r2)
                    },
                    "y_test": y_test.tolist(),
                    "y_pred": y_pred.tolist(),
                    "residuals": residuals
                }

            else:  # Classification
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
                recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
                f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

                roc_auc = 0
                try:
                    if len(np.unique(y_test)) == 2:
                        y_prob = model.predict_proba(X_test)[:, 1]
                        roc_auc = roc_auc_score(y_test, y_prob)
                except:
                    pass

                cm = confusion_matrix(y_test, y_pred).tolist()

                y_prob = None
                try:
                    y_prob = model.predict_proba(X_test)
                    y_prob = y_prob.tolist()
                except:
                    pass

                result = {
                    "model_type": model_type,
                    "task_type": "classification",
                    "training_time_seconds": training_time,
                    "metrics": {
                        "accuracy": float(accuracy),
                        "precision": float(precision),
                        "recall": float(recall),
                        "f1": float(f1),
                        "roc_auc": float(roc_auc)
                    },
                    "y_test": y_test.tolist(),
                    "y_pred": y_pred.tolist(),
                    "y_prob": y_prob,
                    "confusion_matrix": cm
                }

            # Add feature importances if available
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_.tolist()
                feature_importance = {feat: imp for feat, imp in zip(feature_columns, importances)}
                result["feature_importances"] = feature_importance

            # ── Learning / Validation Curve ──────────────────────────────────
            try:
                lc_data    = []
                lc_x_label = "Training Samples"
                is_reg     = (task_type == "regression")
                score_fn   = r2_score if is_reg else accuracy_score
                cls_name   = type(model).__name__

                if cls_name in ("GradientBoostingRegressor", "GradientBoostingClassifier"):
                    # staged_predict: already trained, O(n_estimators) predictions only
                    lc_x_label = "Estimators"
                    n_est      = model.n_estimators
                    step       = max(1, n_est // 20)
                    tr_preds   = list(model.staged_predict(X_train))
                    va_preds   = list(model.staged_predict(X_test))
                    for i in range(step - 1, n_est, step):
                        lc_data.append({
                            "x":           i + 1,
                            "train_score": round(float(score_fn(y_train, tr_preds[i])), 4),
                            "val_score":   round(float(score_fn(y_test,  va_preds[i])), 4),
                        })

                else:
                    # Generic sklearn learning curve — works for every estimator
                    scoring  = "r2" if is_reg else "accuracy"
                    n_total  = len(X)
                    n_pts    = 6 if n_total >= 300 else max(3, n_total // 50)
                    ts, tr_sc, va_sc = sk_learning_curve(
                        get_model(model_type, params, task_type),
                        X, y,
                        train_sizes=np.linspace(0.15, 1.0, n_pts),
                        cv=3,
                        scoring=scoring,
                        n_jobs=1,
                        error_score=0.0,
                    )
                    for size, tr, va in zip(ts, tr_sc.mean(axis=1), va_sc.mean(axis=1)):
                        lc_data.append({
                            "x":           int(size),
                            "train_score": round(float(tr), 4),
                            "val_score":   round(float(va), 4),
                        })

                if lc_data:
                    result["learning_curve"]         = lc_data
                    result["learning_curve_x_label"] = lc_x_label
            except Exception:
                pass  # Learning curve is optional — never fail the main response

            # ── Cross-Validation (5-fold) ─────────────────────────────────────
            try:
                cv_metrics = {}
                cv_folds   = 5

                if task_type == "regression":
                    for sk_scoring, label in [
                        ("r2",                          "r2"),
                        ("neg_mean_absolute_error",     "mae"),
                        ("neg_root_mean_squared_error", "rmse"),
                    ]:
                        cv_s = cross_val_score(
                            get_model(model_type, params, task_type),
                            X, y, cv=cv_folds, scoring=sk_scoring,
                            n_jobs=1, error_score=0.0,
                        )
                        if sk_scoring.startswith("neg_"):
                            cv_s = -cv_s
                        cv_metrics[label] = {
                            "mean":   round(float(cv_s.mean()), 4),
                            "std":    round(float(cv_s.std()),  4),
                            "scores": [round(float(s), 4) for s in cv_s],
                        }

                else:  # classification
                    for sk_scoring, label in [
                        ("accuracy",           "accuracy"),
                        ("f1_weighted",        "f1"),
                        ("precision_weighted", "precision"),
                        ("recall_weighted",    "recall"),
                    ]:
                        cv_s = cross_val_score(
                            get_model(model_type, params, task_type),
                            X, y, cv=cv_folds, scoring=sk_scoring,
                            n_jobs=1, error_score=0.0,
                        )
                        cv_metrics[label] = {
                            "mean":   round(float(cv_s.mean()), 4),
                            "std":    round(float(cv_s.std()),  4),
                            "scores": [round(float(s), 4) for s in cv_s],
                        }

                if cv_metrics:
                    result["cv_scores"] = cv_metrics
            except Exception:
                pass  # CV is optional — never fail the main response

            return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Training error: {str(e)}\n{traceback.format_exc()}"
        )

@app.post("/compare")
async def compare(request_body: List[Dict[str, Any]]):
    """
    Train and compare up to 3 models
    """
    try:
        if len(request_body) > 3:
            raise ValueError("Maximum 3 models allowed for comparison")

        results = []
        for model_request in request_body:
            result = await train(model_request)
            results.append(result)

        return {"models": results}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Comparison error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
