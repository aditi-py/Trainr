# Trainr

A complete no-code machine learning tool. Upload a dataset, pick a model, configure it, train it, and compare results, all without writing a single line of code.

---

## What is Trainr?

Trainr guides you through the full ML lifecycle in 5 steps:

1. **Import Data**: Drag-and-drop or browse for a file (CSV, Excel, Parquet, JSON, TXT). An automatic data profile shows row/column counts, inferred types, null percentages, and a preview of the first rows.
2. **Select Model**: Choose from 30+ models across regression, classification, time series, clustering, and deep learning. Browse by category and read each model's description and complexity rating.
3. **Configure Features**: Select the target column and input features. Set preprocessing options for null imputation and feature scaling. A correlation table highlights relationships and warns about data leakage. Toggle class imbalance handling. Click any type badge to override a column's inferred type.
4. **Set Parameters**: Tune hyperparameters with sliders and dropdowns. One-click presets apply sensible defaults. Configure train/val/test split, cross-validation, bootstrap CI, and auto-tune.
5. **View Results**: Explore metrics, feature importance charts, scatter plots, residuals, confusion matrices (with TP/TN/FP/FN breakdown), ROC curves, PCA cluster views, learning curves, CV scores, and bootstrap CI. Switch to the Predict tab to run inference on new data. Pin up to 3 models to a side-by-side comparison panel. Export HTML reports.

---

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+

### 1 - Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2 - Start the backend (keep this terminal open)

```bash
python server.py
```

The FastAPI backend starts at `http://localhost:8000`. A health-check endpoint is available at `http://localhost:8000/health`.

> **Important:** The backend must be running before you upload a file. The app polls the backend every 5 seconds and shows a red banner if it is unreachable.

### 3 - Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The React dev server starts at `http://localhost:5190`.

### 4 - Open the app

Navigate to `http://localhost:5190` in your browser.

---

## Supported File Formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Any delimiter auto-detected |
| Excel | `.xlsx`, `.xls` | First sheet loaded |
| Parquet | `.parquet` | PyArrow required |
| JSON | `.json` | Array of objects or records format |
| Text | `.txt` | Tab or comma-separated |

Maximum upload size: 500 MB.

---

## Supported Models

### Regression (7 models)
| Model | ID | Notes |
|-------|----|-------|
| Linear Regression | `linear_regression` | Baseline; no tunable params |
| Ridge Regression | `ridge` | L2 regularization; `alpha` |
| Lasso Regression | `lasso` | L1 regularization, feature selection; `alpha` |
| Random Forest Regressor | `random_forest_regressor` | `n_estimators`, `max_depth`, `min_samples_split` |
| XGBoost Regressor | `xgboost_regressor` | `n_estimators`, `learning_rate`, `max_depth`, `subsample`, `colsample_bytree` |
| Gradient Boosting Regressor | `gradient_boosting_regressor` | `n_estimators`, `learning_rate`, `max_depth` |
| Support Vector Regressor | `svr` | `C`, `kernel`, `gamma` |

### Classification (8 models)
| Model | ID | Notes |
|-------|----|-------|
| Logistic Regression | `logistic_regression` | `C`, `max_iter`, `solver`; supports `class_weight` |
| Random Forest Classifier | `random_forest_classifier` | `n_estimators`, `max_depth`, `min_samples_split`; supports `class_weight` |
| XGBoost Classifier | `xgboost_classifier` | `n_estimators`, `learning_rate`, `max_depth` |
| Support Vector Machine | `svm_classifier` | `C`, `kernel`, `gamma`; supports `class_weight` |
| K-Nearest Neighbors | `knn` | `n_neighbors` |
| Naive Bayes | `naive_bayes` | No tunable params |
| Gradient Boosting Classifier | `gradient_boosting_classifier` | `n_estimators`, `learning_rate`, `max_depth` |
| Decision Tree Classifier | `decision_tree_classifier` | `max_depth`, `min_samples_split` |

### Time Series (3 models)
| Model | ID | Notes |
|-------|----|-------|
| ARIMA | `arima` | `p`, `d`, `q` |
| SARIMA | `sarima` | `p`, `d`, `q`, `P`, `D`, `Q`, `m` |
| Exponential Smoothing | `exponential_smoothing` | `trend`, `seasonal`, `seasonal_periods` |

### Clustering (3 models)
| Model | ID | Notes |
|-------|----|-------|
| K-Means | `kmeans` | `n_clusters`, `init`, `max_iter` |
| DBSCAN | `dbscan` | `eps`, `min_samples` |
| Hierarchical Clustering | `hierarchical` | `n_clusters`, `linkage` (ward / complete / average / single) |

### Deep Learning (4 models, optional TensorFlow)
| Model | ID | Notes |
|-------|----|-------|
| Multi-Layer Perceptron | `mlp` | `units`, `layers`, `dropout`, `activation`, `optimizer`, `learning_rate`, `epochs`, `batch_size` |
| LSTM | `lstm` | All MLP params plus `bidirectional`, `return_sequences`, `stateful` |
| CNN-1D | `cnn_1d` | `units`, `layers`, `dropout`, `activation`, `optimizer`, `learning_rate`, `epochs`, `batch_size` |
| Autoencoder | `autoencoder` | `units`, `layers`, `dropout`, `activation`, `optimizer`, `learning_rate`, `epochs` |

All deep learning models also support: `weight_init`, `lr_scheduler`, `loss`, `validation_split`, `early_stopping`, `patience`, and regularization (`reg_type`, `reg_lambda`).

Deep learning models are skipped gracefully if TensorFlow is not installed.

---

## Features

### Step 1 - Data Import

- Drag-and-drop zone or format-specific file picker buttons (CSV / Excel / Parquet / JSON / TXT)
- Automatic data profiling on upload:
  - Row x column count
  - Per-column inferred type (numeric, categorical, datetime, text)
  - Null count and null percentage per column
  - Unique value count per column
  - Value distribution for columns with 30 or fewer unique values (used for imbalance detection)
- Preview of the first 10 rows in a scrollable table
- Backend health polled every 5 seconds; red banner shown when unreachable and cleared automatically once backend is up

---

### Step 2 - Select Model

- Category tabs: Regression | Classification | Clustering | Time Series | Deep Learning
- Each model card shows a short description, complexity badge (Low / Med / High), and a best-use tooltip
- Browse models freely and select the one that fits your task

---

### Step 3 - Configure Features

#### Feature Selection
- Checkbox list of all columns; toggle individually or select/deselect all
- Target column dropdown
- Date column picker (time series only)

#### Preprocessing Controls
Users choose how each preprocessing step behaves before training. These settings are applied in order:

**Null Imputation (Numeric columns)**

| Option | Behaviour |
|--------|-----------|
| Median (default) | Fill nulls with the column median |
| Mean | Fill nulls with the column mean |
| Zero | Fill nulls with 0 |
| Drop rows | Remove any row that has a null in a numeric feature column |

**Null Imputation (Categorical columns)**

| Option | Behaviour |
|--------|-----------|
| Mode (default) | Fill nulls with the most frequent value |
| "unknown" | Fill nulls with the literal string "unknown" |
| Drop rows | Remove any row that has a null in a categorical feature column |

**Feature Scaling**

| Option | Behaviour |
|--------|-----------|
| None (default) | No scaling applied |
| Standard (z-score) | Subtract mean, divide by std (StandardScaler) |
| Min-Max | Scale each column to [0, 1] (MinMaxScaler) |
| Robust | Scale using median and IQR, robust to outliers (RobustScaler) |

Scaling is applied to numeric feature columns only, after null imputation and label encoding. The fitted scaler is stored and reapplied automatically when running predictions from the Predict tab.

#### Column Type Override
Every feature shows a clickable type badge (Num / Cat / Txt). Click to cycle through types:

```
numeric -> categorical -> text -> numeric -> ...
```

- Overridden columns are highlighted in magenta with an edit indicator
- Overrides are applied in the preprocessing pipeline before null handling and encoding
- A "Reset type overrides" button clears all changes at once
- Use this to force a numeric ID column to be treated as a category, or to ensure a text column is label-encoded

#### Correlation Analysis
- Pearson correlation of each numeric feature with the target
- Color-coded correlation bars
- Top correlated features highlighted in a suggestion chip

#### Data Leakage Warnings
Dismissible warning cards are shown for:
- **Near-perfect correlation**: any feature with |r| > 0.98 with the target is flagged as suspicious
- **ID / index columns**: any feature whose unique count equals the total row count is flagged as likely an identifier

#### Class Imbalance Handling (Classification Only)
When the target column has 30 or fewer unique values, a class distribution bar chart appears showing:
- Class counts and percentages
- Imbalance ratio badge (shown when max class / min class > 3)

Three strategies are available:

| Strategy | Effect |
|----------|--------|
| None (default) | No adjustment |
| Class Weights | Sets `class_weight="balanced"` on compatible models (Logistic Regression, Random Forest, SVM). Penalises misclassification of minority classes more heavily. |
| SMOTE | Synthetic Minority Over-sampling Technique. Generates synthetic minority-class samples to balance the training set. Requires `imbalanced-learn` (`pip install imbalanced-learn`). |

---

### Step 4 - Set Parameters

#### Quick Presets
Three one-click presets apply sensible defaults:
- **Conservative**: simpler models, fewer estimators, higher regularisation
- **Balanced**: moderate complexity (recommended starting point)
- **Aggressive**: more estimators, lower regularisation, higher complexity

#### Hyperparameter Controls
Each model exposes its relevant parameters as sliders, dropdowns, or toggles. Every control has a plain-English tooltip explaining what the parameter does and when to change it.

#### 3-Way Data Split
A visual split bar shows the exact breakdown of your data:
- **Test size** slider (10-40%, default 20%): held out for final evaluation
- **Validation size** slider (0-30%, default 10%): used for early stopping in deep learning; optional for classical models
- Row counts and percentages update live
- Constraint: val_size + test_size must be 90% or less

#### Cross-Validation
- Toggle to enable k-fold CV
- Quick-select buttons: 3 / 5 / 10 folds
- Classification uses `StratifiedKFold` (preserves class balance per fold)
- Time series uses `TimeSeriesSplit` (respects temporal order)
- Results show mean +/- std per metric plus per-fold individual scores

#### Bootstrap Confidence Intervals
- Toggle to add 95% bootstrap CI to results
- 100 bootstrap samples drawn from the test set; roughly 5-10 seconds added to training time
- Reports: mean, std, lower bound (2.5th percentile), upper bound (97.5th percentile)

#### Auto-Tune (GridSearchCV)
Available for all classical regression and classification models (not DL, clustering, or time series):

| Preset | CV Folds | Typical Time |
|--------|----------|--------------|
| Fast | 3 | 10-30 s |
| Thorough | 5 | 30-90 s |

Hyperparameter grids searched per model:

| Model | Grid |
|-------|------|
| Ridge / Lasso | `alpha` (5 values) |
| SVR | `C` x `kernel` (6 combos) |
| Random Forest (both) | `n_estimators` x `max_depth` (9 combos) |
| Gradient Boosting (both) | `n_estimators` x `learning_rate` x `max_depth` (12 combos) |
| XGBoost (both) | `n_estimators` x `learning_rate` x `max_depth` (12 combos) |
| Logistic Regression | `C` (4 values) |
| SVM | `C` x `kernel` (6 combos) |
| KNN | `n_neighbors` (5 values) |

Best parameters are automatically applied to the final model. The Results tab shows which parameters were chosen, the best CV score, search time, and number of candidates evaluated.

---

### Step 5 - View Results

#### Results Tab

**Header and Summary**
- Model name and training timestamp
- Overfitting health badge:

| Badge | Condition |
|-------|-----------|
| Healthy (green) | train_score minus test_score is less than 0.05 |
| Mild Overfit (amber) | delta is between 0.05 and 0.15 |
| Severe Overfit (red) | delta is 0.15 or greater |

**Metric Cards**

| Task | Metrics |
|------|---------|
| Regression | R2, MAE, MSE, RMSE, MAPE |
| Classification | Accuracy, Precision, Recall, F1, AUC-ROC |
| Clustering | Silhouette Score, Inertia |
| Time Series | MSE, RMSE, MAE |

Each card is color-coded: green (good), amber (fair), red (poor) based on metric-specific thresholds.

**Train vs Test Score**
Side-by-side display of train score and test score with color coding (cyan for train, amber for test).

**Bootstrap CI**
When enabled, displays the metric mean +/- std with a 95% confidence interval range and bootstrap sample count.

**Cross-Validation Scores**
When enabled, shows per-metric rows with mean +/- std and a per-fold bar chart color-coded by performance range.

**Auto-Tune Results**
When auto-tune was enabled, a card shows:
- Best parameters found
- Best CV score achieved
- Number of candidates evaluated
- Search duration

**Class Distribution**
For classification tasks, a bar chart shows the training-set class distribution with counts, percentages, and imbalance ratio.

**Visualisations**

| Chart | When Shown |
|-------|-----------|
| Actual vs Predicted scatter plot | Regression / Classification |
| Residual histogram | Regression |
| Feature Importance bar chart (top 20) | Tree-based models |
| Confusion matrix with TP/TN/FP/FN | Classification |
| ROC curve | Binary classification |
| PCA 2D cluster scatter | Clustering |
| Training / Validation learning curve | Deep learning (epochs on X-axis) |
| Training / Validation learning curve | Classical models (training set size on X-axis) |

**Confusion Matrix Breakdown**
For binary classification, four cards below the matrix show:
- **TP** (True Positive): correctly predicted positive
- **TN** (True Negative): correctly predicted negative
- **FP** (False Positive): predicted positive, actually negative (Type I error)
- **FN** (False Negative): predicted negative, actually positive (Type II error)

For multi-class classification, a per-class table shows TP, TN, FP, FN computed using a one-vs-rest approach.

**Threshold Tuner** (binary classification with probabilities)
- Slider adjusts the classification threshold from 0.0 to 1.0 (default 0.5)
- Confusion matrix, Precision, Recall, F1, and Accuracy update in real time
- Use this to optimise for recall (lower threshold) or precision (higher threshold)

---

#### Predict Tab

Appears alongside the Results tab after a model has been trained.

- **Input form**: one field per feature, pre-filled with the training-set mean for numeric columns
- Field types adapt to the column: numeric input, text input, or dropdown for low-cardinality categories
- **Run Prediction**: sends inputs to the backend `/predict` endpoint; returns the predicted value/label and, for classification, the probability and per-class probabilities
- **Prediction history**: keeps the last 20 predictions in the session for comparison

---

#### Model Comparison

- Click **+ Compare** on any Results screen to add the current model (up to 3 total)
- A side-by-side table appears showing all metrics across all pinned models
- The best value in each row is highlighted in cyan
- **Export Comparison** generates a self-contained HTML report with the comparison table and individual model detail cards

---

### Export

| Export | What It Contains |
|--------|-----------------|
| **HTML Report** | Model overview, metrics table, hyperparameters, feature configuration, all charts (as data tables), appendix with top rows of each result set |
| **JSON Snapshot** | Raw result object with all metrics, predictions, feature stats, CV scores, bootstrap CI, and auto-tune details |
| **Comparison HTML Report** | Side-by-side metrics with best-value highlighting and per-model detail cards for all compared models |

HTML reports are fully self-contained (embedded CSS, no external dependencies) and print-friendly.

---

### Preprocessing Pipeline

Users configure each of these steps in the Configure Features step (Step 3) before training:

1. **Type overrides**: applied first; `"categorical"` / `"text"` converts numeric columns to string; `"numeric"` coerces object columns to float
2. **Null imputation (numeric)**: median / mean / zero / drop rows (user-selected per run)
3. **Null imputation (categorical)**: mode / "unknown" constant / drop rows (user-selected per run)
4. **Label encoding**: all categorical / text columns encoded with `LabelEncoder`; target column encoded separately if categorical
5. **Feature scaling**: none / standard (z-score) / min-max / robust (user-selected per run); applied to numeric feature columns only
6. **SMOTE** (if selected): applied to training data only after the train/val/test split
7. **Class weights** (if selected): injected into the model constructor for supported classifiers

All encoders, the fitted scaler, and feature statistics (min, max, mean per column) are stored alongside the trained model and reapplied automatically when running predictions from the Predict tab.

---

## Architecture

### Backend (`backend/server.py`)

- **Framework**: FastAPI + Uvicorn
- **Session management**:
  - `SESSIONS`: in-memory dict keyed by `file_id` UUID; stores uploaded DataFrames
  - `MODEL_STORE`: in-memory dict keyed by `predict_id` UUID; stores trained models, encoders, scaler, and feature stats
  - Both stores persist for the lifetime of the backend process
- **Preprocessing pipeline**: user-controlled null imputation, label encoding, and feature scaling via sklearn; column type overrides; imbalanced-learn SMOTE (optional)

**Endpoints**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| POST | `/upload` | Parse file, store DataFrame, return profile |
| POST | `/train` | Train one model, return metrics + chart data + predict_id |
| POST | `/predict` | Run inference on a single row using a stored model |
| POST | `/compare` | Train up to 3 models, return all results |

**Train request fields** (preprocessing-related):

| Field | Type | Options | Default |
|-------|------|---------|---------|
| `preproc_null_numeric` | string | `median`, `mean`, `zero`, `drop` | `median` |
| `preproc_null_cat` | string | `mode`, `unknown`, `drop` | `mode` |
| `preproc_scaling` | string | `none`, `standard`, `minmax`, `robust` | `none` |
| `type_overrides` | object | `{col: "numeric"|"categorical"|"text"}` | `{}` |

### Frontend (`frontend/src/App.jsx`)

- **Framework**: React 18 + Vite
- **State**: single `useReducer` with an `initialState` object; no external state library
- **Charts**: Recharts (LineChart, ScatterChart, BarChart, ResponsiveContainer)
- **Styling**: 100% inline styles; design token object `t` derived from dark/light mode flag

**Key components**

| Component | Responsibility |
|-----------|---------------|
| `StepImport` | File upload, drag-and-drop, data profile card |
| `StepModel` | Model picker with category tabs |
| `StepFeatures` | Feature selector, preprocessing controls, correlation table, leakage warnings, type override badges, class imbalance UI |
| `StepParams` | Hyperparameter form, presets, split slider, CV toggle, bootstrap toggle, auto-tune card |
| `StepResults` | Metric cards, all chart panels, confusion matrix with TP/TN/FP/FN, threshold tuner, learning curve, CV scores, auto-tune results, class distribution, comparison table, predict tab, export buttons |
| `BottomBar` | Sticky navigation bar with contextual disabled-button hints |
| `CyberIcon` | Inline SVG icon component (upload, cpu, hex, sliders, chart, warn, close, check, info) |
| `CyberpunkBackground` | Matrix rain canvas animation |
| `Navbar` / `Sidebar` | Step navigation with progress state |
| `ToastContainer` | Auto-dismissing notification stack |

---

## Project Structure

```
Trainr/
+-- backend/
|   +-- server.py            # FastAPI application (single file)
|   +-- requirements.txt     # Python dependencies
+-- frontend/
|   +-- src/
|   |   +-- App.jsx          # React application (single component file)
|   +-- index.html           # HTML entry point
|   +-- package.json         # Node dependencies
|   +-- vite.config.js       # Vite configuration
+-- README.md
```

---

## Configuration

### Ports

| Service | Default URL | Config location |
|---------|------------|----------------|
| Backend | `http://localhost:8000` | Top of `backend/server.py` |
| Frontend | `http://localhost:5190` | `frontend/vite.config.js` |

### CORS
The backend allows requests from all origins (`*`) for development. Restrict this for production deployment.

### TensorFlow (optional)
```bash
pip install tensorflow
```
Without it the app works fully; only MLP, LSTM, CNN-1D, and Autoencoder are unavailable.

### SMOTE / imbalanced-learn (optional)
```bash
pip install imbalanced-learn
```
Without it the SMOTE strategy option is visible but falls back to no-op with a backend warning. Class Weights and None strategies still work.

---

## Troubleshooting

### Backend not starting
- Check Python version: `python --version` (need 3.8+)
- Install deps: `pip install -r backend/requirements.txt`
- Check port conflict: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (macOS/Linux)
- The app shows a red banner at the top if the backend is unreachable; it polls every 5 seconds and clears automatically once the backend is up

### "Failed to fetch" on file upload
- The backend is not running. Start it: `cd backend && python server.py`
- After starting, the red banner disappears within 5 seconds; no page reload needed
- Re-select and upload your file; the previous failed upload is not retained

### Next Step button is disabled
A magenta hint above the button explains why:
- "Start the backend first": backend is not running
- "Upload a file to continue": no file uploaded yet
- "Select a model to continue": on step 2
- "Choose a target column and at least one feature": on step 3
- On step 4 (Set Parameters), clicking Train advances to step 5

### Training is very slow
- Large datasets (more than 50k rows) with ensemble models (Random Forest, XGBoost) take longer
- Auto-tune multiplies training time by the number of parameter combinations x CV folds; use Fast (3-fold) mode on first runs
- Bootstrap CI adds roughly 5-10 seconds; disable if not needed
- Deep learning: reduce `epochs` or increase `batch_size` to speed up

### SMOTE error during training
- Install `imbalanced-learn`: `pip install imbalanced-learn`
- SMOTE requires at least 2 samples per minority class after the train split; use a larger dataset or switch to Class Weights

### Predict tab not appearing
- The Predict tab is only shown after a model has been successfully trained in the current session
- If you refresh the page, the model session is lost; re-train to get the Predict tab back

### Frontend shows blank page
- Ensure backend is running
- Hard refresh: `Ctrl+Shift+R`
- Open DevTools (F12) and check the Console tab for errors

### File upload fails
- Confirm the file matches a supported format/extension
- For large files (more than 50 MB) you may need to increase the server body size limit in `server.py`

### TensorFlow errors
- Install: `pip install tensorflow`
- On Apple Silicon: `pip install tensorflow-macos`
- GPU setup is not required; TensorFlow runs on CPU by default

---

## License

MIT License

## Author

Built by Aditi (aditi-py)
