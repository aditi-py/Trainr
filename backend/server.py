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
from sklearn.model_selection import (
    train_test_split, cross_val_score, KFold, StratifiedKFold,
    TimeSeriesSplit, learning_curve as sk_learning_curve
)
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

def get_model(model_type: str, params: Dict[str, Any], task_type: str, n_features: int = 1):
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

    # Deep Learning Models
    elif model_type in ("mlp", "lstm", "cnn_1d", "autoencoder"):
        if not TENSORFLOW_AVAILABLE:
            raise ValueError("TensorFlow not installed. Install with: pip install tensorflow")
        return _build_dl_model(model_type, params, task_type, n_features)

    else:
        raise ValueError(f"Unknown model type: {model_type}")


def _build_dl_model(model_type: str, params: dict, task_type: str, n_features: int):
    """Build and compile a Keras deep learning model."""
    units      = params.get("units", 64)
    layers_n   = max(1, params.get("layers", 2))
    dropout    = params.get("dropout", 0.2)
    activation = params.get("activation", "relu" if model_type != "lstm" else "tanh")
    lr         = params.get("learning_rate", 0.001)
    opt_name   = params.get("optimizer", "adam")
    is_cls     = (task_type == "classification")
    loss       = params.get("loss", "binary_crossentropy" if is_cls else "mse")

    # ── Build architecture ────────────────────────────────────────────
    model = Sequential()

    if model_type == "mlp":
        model.add(layers.Dense(units, activation=activation, input_shape=(n_features,)))
        for _ in range(layers_n - 1):
            model.add(layers.Dense(units, activation=activation))
            model.add(layers.Dropout(dropout))

    elif model_type == "lstm":
        bidir = params.get("bidirectional", False)
        for i in range(layers_n):
            ret_seq = (i < layers_n - 1)
            lyr = layers.LSTM(units, activation=activation, return_sequences=ret_seq,
                              input_shape=(1, n_features) if i == 0 else None)
            model.add(layers.Bidirectional(lyr) if bidir else lyr)
            if i > 0:
                model.add(layers.Dropout(dropout))

    elif model_type == "cnn_1d":
        model.add(layers.Conv1D(filters=units, kernel_size=1, activation=activation,
                                input_shape=(1, n_features)))
        for _ in range(layers_n - 1):
            model.add(layers.Conv1D(filters=units, kernel_size=1, activation=activation))
            model.add(layers.Dropout(dropout))
        model.add(layers.Flatten())
        model.add(layers.Dense(64, activation=activation))

    elif model_type == "autoencoder":
        # Encoder
        model.add(layers.Dense(units, activation=activation, input_shape=(n_features,)))
        for _ in range(layers_n - 1):
            model.add(layers.Dense(max(4, units // 2), activation=activation))
            model.add(layers.Dropout(dropout))
        # Bottleneck
        model.add(layers.Dense(max(2, units // 4), activation=activation))
        # Decoder
        for _ in range(layers_n - 1):
            model.add(layers.Dense(max(4, units // 2), activation=activation))
            model.add(layers.Dropout(dropout))

    # ── Output layer ──────────────────────────────────────────────────
    if is_cls:
        model.add(layers.Dense(1, activation="sigmoid"))
    else:
        model.add(layers.Dense(1))

    # ── Compile ───────────────────────────────────────────────────────
    optimizers = {
        "adam":    keras.optimizers.Adam,
        "sgd":     keras.optimizers.SGD,
        "rmsprop": keras.optimizers.RMSprop,
        "adamw":   keras.optimizers.AdamW if hasattr(keras.optimizers, "AdamW") else keras.optimizers.Adam,
        "adagrad": keras.optimizers.Adagrad,
    }
    opt = optimizers.get(opt_name, keras.optimizers.Adam)(learning_rate=lr)
    model.compile(optimizer=opt, loss=loss,
                  metrics=["accuracy" if is_cls else "mse"])
    model._hm_keras = True
    return model

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
        val_size = request_body.get("val_size", 0.0)      # 0 = no explicit val set
        cv_folds = request_body.get("cv_folds", None)
        bootstrap = request_body.get("bootstrap", False)

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

        # For deep learning models, infer task type from target variable if not explicitly a classifier
        if model_type in ["mlp", "lstm", "cnn_1d", "autoencoder"] and task_type == "regression":
            # Check target column to infer: few unique values = classification
            unique_vals = len(df[target_column].unique())
            if unique_vals <= 10 and unique_vals <= len(df) * 0.1:
                task_type = "classification"

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

            # ── 3-way split: train / val / test ──────────────────────────────
            # First carve out the test set
            X_tv, X_test, y_tv, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            # Then optionally carve out a validation set from the train pool
            if val_size and val_size > 0:
                # val_size is a fraction of the ORIGINAL data; adjust relative to tv pool
                val_frac = val_size / (1.0 - test_size)
                val_frac = min(max(val_frac, 0.05), 0.5)   # clamp to sane range
                X_train, X_val, y_train, y_val = train_test_split(
                    X_tv, y_tv, test_size=val_frac, random_state=42
                )
            else:
                X_train, y_train = X_tv, y_tv
                X_val,  y_val    = X_test, y_test   # fall back to test for val display

            # Get and train model
            n_features = X_train.shape[1]
            model = get_model(model_type, params, task_type, n_features=n_features)

            # Check if it's a deep learning model
            is_dl = hasattr(model, '_hm_keras') and model._hm_keras
            dl_lc = []

            if is_dl:
                # Deep learning model: reshape data for Keras
                # Keras expects (samples, timesteps, features) for LSTM/CNN, or (samples, features) for Dense
                if model_type == "lstm" or model_type == "cnn_1d":
                    X_train_dl = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
                    X_test_dl = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
                else:
                    X_train_dl = X_train
                    X_test_dl = X_test

                epochs = params.get("epochs", 50)
                batch_size = params.get("batch_size", 32)
                validation_split = params.get("validation_split", 0.1)

                # Train the model with verbose=0 to suppress output
                history = model.fit(
                    X_train_dl, y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=validation_split,
                    verbose=0
                )
                training_time = time.time() - start_time
                y_pred = model.predict(X_test_dl, verbose=0).flatten()

                # Extract training history as learning curve
                dl_history = history.history
                loss_key = "loss"
                val_loss_key = "val_loss"
                if loss_key in dl_history and val_loss_key in dl_history:
                    dl_lc = []
                    for epoch_i, (tl, vl) in enumerate(zip(dl_history[loss_key], dl_history[val_loss_key])):
                        dl_lc.append({
                            "x": epoch_i + 1,
                            "train_score": round(float(tl), 4),
                            "val_score": round(float(vl), 4),
                        })
            else:
                # sklearn model: standard fit
                model.fit(X_train, y_train)
                training_time = time.time() - start_time
                y_pred = model.predict(X_test)

            # ── Train score (for overfitting detection) ───────────────────────
            try:
                if is_dl:
                    X_tr_dl = X_train.reshape((X_train.shape[0], 1, X_train.shape[1])) \
                              if model_type in ("lstm", "cnn_1d") else X_train
                    y_train_pred = model.predict(X_tr_dl, verbose=0).flatten()
                    if task_type == "classification":
                        y_train_pred = (y_train_pred > 0.5).astype(int)
                else:
                    y_train_pred = model.predict(X_train)

                if task_type == "regression":
                    train_score = float(r2_score(y_train, y_train_pred))
                    test_score  = float(r2_score(y_test,  y_pred))
                else:
                    train_score = float(accuracy_score(y_train, y_train_pred))
                    test_score  = float(accuracy_score(y_test,
                                    (y_pred > 0.5).astype(int) if is_dl else y_pred))
            except Exception:
                train_score, test_score = None, None

            if task_type == "regression":
                # Regression metrics (on TEST set)
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
                    "train_score": train_score,
                    "test_score":  test_score,
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
                # For deep learning, y_pred might be probabilities; threshold them
                if is_dl and np.max(y_pred) <= 1.0 and np.min(y_pred) >= 0:
                    y_pred_binary = (y_pred > 0.5).astype(int).flatten()
                else:
                    y_pred_binary = y_pred

                accuracy = accuracy_score(y_test, y_pred_binary)
                precision = precision_score(y_test, y_pred_binary, average="weighted", zero_division=0)
                recall = recall_score(y_test, y_pred_binary, average="weighted", zero_division=0)
                f1 = f1_score(y_test, y_pred_binary, average="weighted", zero_division=0)

                roc_auc = 0
                try:
                    if len(np.unique(y_test)) == 2:
                        if is_dl:
                            y_prob = y_pred.flatten()
                        else:
                            y_prob = model.predict_proba(X_test)[:, 1]
                        roc_auc = roc_auc_score(y_test, y_prob)
                except:
                    pass

                cm = confusion_matrix(y_test, y_pred_binary).tolist()

                y_prob = None
                try:
                    if is_dl:
                        y_prob = y_pred.flatten().tolist()
                    else:
                        y_prob = model.predict_proba(X_test)
                        y_prob = y_prob.tolist()
                except:
                    pass

                result = {
                    "model_type": model_type,
                    "task_type": "classification",
                    "training_time_seconds": training_time,
                    "train_score": train_score,
                    "test_score":  test_score,
                    "metrics": {
                        "accuracy": float(accuracy),
                        "precision": float(precision),
                        "recall": float(recall),
                        "f1": float(f1),
                        "roc_auc": float(roc_auc)
                    },
                    "y_test": y_test.tolist(),
                    "y_pred": y_pred_binary.tolist() if hasattr(y_pred_binary, 'tolist') else y_pred_binary,
                    "y_prob": y_prob,
                    "confusion_matrix": cm
                }

            # Add feature importances if available
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_.tolist()
                feature_importance = {feat: imp for feat, imp in zip(feature_columns, importances)}
                result["feature_importances"] = feature_importance

            # Add DL training history as learning curve
            if is_dl and dl_lc:
                result["learning_curve"] = dl_lc
                result["learning_curve_x_label"] = "Epoch (Loss)"

            # ── Learning / Validation Curve ──────────────────────────────────
            if not is_dl:
                try:
                    lc_data    = []
                    lc_x_label = "Training Samples"
                    is_reg     = (task_type == "regression")
                    score_fn   = r2_score if is_reg else accuracy_score
                    cls_name   = type(model).__name__

                    if cls_name in ("GradientBoostingRegressor", "GradientBoostingClassifier"):
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
                        scoring  = "r2" if is_reg else "accuracy"
                        n_total  = len(X)
                        n_pts    = 6 if n_total >= 300 else max(3, n_total // 50)
                        ts, tr_sc, va_sc = sk_learning_curve(
                            get_model(model_type, params, task_type, n_features=n_features),
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

            # ── Cross-Validation ──────────────────────────────────────────────
            if not is_dl:
                try:
                    cv_metrics = {}
                    k = int(cv_folds) if cv_folds else 5

                    # Choose splitter based on task type
                    if task_type == "time_series":
                        cv_splitter = TimeSeriesSplit(n_splits=k)
                    elif task_type == "classification":
                        cv_splitter = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
                    else:
                        cv_splitter = KFold(n_splits=k, shuffle=True, random_state=42)

                    if task_type == "regression":
                        for sk_scoring, label in [
                            ("r2",                          "r2"),
                            ("neg_mean_absolute_error",     "mae"),
                            ("neg_root_mean_squared_error", "rmse"),
                        ]:
                            cv_s = cross_val_score(
                                get_model(model_type, params, task_type, n_features=n_features),
                                X, y, cv=cv_splitter, scoring=sk_scoring,
                                n_jobs=1, error_score=0.0,
                            )
                            if sk_scoring.startswith("neg_"):
                                cv_s = -cv_s
                            cv_metrics[label] = {
                                "mean":   round(float(cv_s.mean()), 4),
                                "std":    round(float(cv_s.std()),  4),
                                "scores": [round(float(s), 4) for s in cv_s],
                            }

                    elif task_type == "classification":
                        for sk_scoring, label in [
                            ("accuracy",           "accuracy"),
                            ("f1_weighted",        "f1"),
                            ("precision_weighted", "precision"),
                            ("recall_weighted",    "recall"),
                        ]:
                            cv_s = cross_val_score(
                                get_model(model_type, params, task_type, n_features=n_features),
                                X, y, cv=cv_splitter, scoring=sk_scoring,
                                n_jobs=1, error_score=0.0,
                            )
                            cv_metrics[label] = {
                                "mean":   round(float(cv_s.mean()), 4),
                                "std":    round(float(cv_s.std()),  4),
                                "scores": [round(float(s), 4) for s in cv_s],
                            }

                    if cv_metrics:
                        result["cv_scores"] = cv_metrics
                        result["cv_k"] = k
                except Exception:
                    pass  # CV is optional

            # ── Bootstrap Confidence Intervals ────────────────────────────────
            if bootstrap and not is_dl:
                try:
                    rng = np.random.default_rng(42)
                    n_boot = 100
                    boot_scores = []
                    is_reg = (task_type == "regression")
                    for _ in range(n_boot):
                        idx = rng.integers(0, len(X_test), size=len(X_test))
                        Xb, yb = X_test[idx], y_test[idx]
                        pb = model.predict(Xb)
                        if is_reg:
                            boot_scores.append(float(r2_score(yb, pb)))
                        else:
                            pb_cls = (pb > 0.5).astype(int) if is_dl else pb
                            boot_scores.append(float(accuracy_score(yb, pb_cls)))
                    boot_scores = np.array(boot_scores)
                    ci_lo = float(np.percentile(boot_scores, 2.5))
                    ci_hi = float(np.percentile(boot_scores, 97.5))
                    result["bootstrap_ci"] = {
                        "mean":    round(float(boot_scores.mean()), 4),
                        "std":     round(float(boot_scores.std()),  4),
                        "ci_lo":   round(ci_lo, 4),
                        "ci_hi":   round(ci_hi, 4),
                        "n":       n_boot,
                        "metric":  "r2" if is_reg else "accuracy",
                    }
                except Exception:
                    pass  # Bootstrap is optional

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
