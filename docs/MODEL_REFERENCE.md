# Trainr - Supported Models Reference

## Regression Models (7 total)

### Linear Regression
**Description:** The simplest linear model. Fits a straight line through the data.
- **Best for:** Small datasets, interpretability is key, linear relationships
- **Complexity:** Low
- **Training time:** Very fast
- **Parameters:** None (uses defaults)
- **Key metric:** R² (higher is better)

### Ridge Regression
**Description:** Linear regression with L2 regularization to prevent overfitting.
- **Best for:** High-dimensional data, correlated features
- **Complexity:** Low
- **Key parameter:** `alpha` (regularization strength)
- **Key metric:** R²

### Lasso Regression
**Description:** Linear regression with L1 regularization. Can shrink some coefficients to zero.
- **Best for:** Feature selection, sparse models
- **Complexity:** Low
- **Key parameter:** `alpha` (regularization strength)
- **Key metric:** R²

### Random Forest Regressor
**Description:** Ensemble of decision trees. Robust and handles non-linear relationships.
- **Best for:** General-purpose regression, datasets with mixed feature types
- **Complexity:** Medium
- **Key parameters:**
  - `n_estimators` (number of trees, 10-500)
  - `max_depth` (tree depth limit, 1-30)
  - `min_samples_split` (minimum samples to split, 2-20)
- **Key metric:** R²

### XGBoost Regressor
**Description:** Gradient boosted trees. State-of-the-art performance, handles outliers well.
- **Best for:** Competitive ML, structured data, when accuracy is critical
- **Complexity:** Medium-High
- **Key parameters:**
  - `learning_rate` (0.01-0.3)
  - `n_estimators` (50-500)
  - `max_depth` (1-15)
  - `subsample` (0.5-1.0)
  - `colsample_bytree` (0.5-1.0)
- **Key metric:** R²
- **Note:** Often produces best results

### Gradient Boosting Regressor
**Description:** Sequential ensemble building. Similar to XGBoost but pure sklearn implementation.
- **Best for:** Robust predictions, more interpretable than XGBoost
- **Complexity:** Medium-High
- **Key parameters:**
  - `learning_rate` (0.01-0.3)
  - `n_estimators` (50-300)
  - `max_depth` (1-15)
- **Key metric:** R²

### Support Vector Regressor (SVR)
**Description:** Finds optimal hyperplane with maximum margin. Handles non-linear data.
- **Best for:** Small to medium datasets, non-linear relationships
- **Complexity:** Medium
- **Key parameters:**
  - `C` (regularization, 0.01-10)
  - `kernel` (linear, rbf, poly)
  - `gamma` (kernel coefficient)
- **Key metric:** R²

---

## Classification Models (8 total)

### Logistic Regression
**Description:** Linear classifier. Outputs probability of class membership.
- **Best for:** Binary classification, interpretability, baseline model
- **Complexity:** Low
- **Key parameters:**
  - `C` (regularization, 0.01-10, higher = less regularization)
  - `max_iter` (100-1000)
  - `solver` (lbfgs, liblinear, etc.)
- **Key metric:** Accuracy, F1

### Random Forest Classifier
**Description:** Ensemble of decision trees. Robust and handles imbalanced data.
- **Best for:** General-purpose classification, non-linear boundaries
- **Complexity:** Medium
- **Key parameters:**
  - `n_estimators` (10-500)
  - `max_depth` (1-30)
  - `min_samples_split` (2-20)
- **Key metric:** F1, ROC-AUC

### XGBoost Classifier
**Description:** Gradient boosted trees for classification. Excellent performance.
- **Best for:** Competitive ML, complex decision boundaries, when accuracy is critical
- **Complexity:** Medium-High
- **Key parameters:**
  - `learning_rate` (0.01-0.3)
  - `n_estimators` (50-500)
  - `max_depth` (1-15)
  - `scale_pos_weight` (for imbalanced data)
- **Key metric:** F1, ROC-AUC
- **Note:** Often produces best results

### Support Vector Machine (SVM)
**Description:** Finds optimal separating hyperplane. Handles high-dimensional data.
- **Best for:** Binary and multi-class problems, text classification
- **Complexity:** Medium
- **Key parameters:**
  - `C` (0.01-10)
  - `kernel` (linear, rbf, poly)
  - `gamma` (kernel coefficient)
- **Key metric:** Accuracy, F1

### K-Nearest Neighbors (KNN)
**Description:** Instance-based learner. Classifies based on nearest neighbors.
- **Best for:** Quick baseline, interpretable decisions, non-linear boundaries
- **Complexity:** Low (training) / Medium (prediction)
- **Key parameters:**
  - `n_neighbors` (3-20, typically 3-5)
  - `weights` (uniform or distance-based)
- **Key metric:** Accuracy, F1
- **Warning:** Slow on large datasets

### Naive Bayes
**Description:** Probabilistic classifier based on Bayes' theorem.
- **Best for:** Text classification, spam detection, fast training
- **Complexity:** Very Low
- **Parameters:** None (uses defaults)
- **Key metric:** Accuracy, F1

### Gradient Boosting Classifier
**Description:** Sequential ensemble. More interpretable than XGBoost.
- **Best for:** Structured data, when explainability matters
- **Complexity:** Medium-High
- **Key parameters:**
  - `learning_rate` (0.01-0.3)
  - `n_estimators` (50-300)
  - `max_depth` (1-15)
- **Key metric:** F1, ROC-AUC

---

## Time Series Models (3 total)

### ARIMA
**Description:** AutoRegressive Integrated Moving Average. Classic time series model.
- **Best for:** Univariate time series, stationary or differenced data
- **Complexity:** Medium
- **Key parameters:**
  - `p` (AR order, 0-5): Past values used
  - `d` (differencing, 0-2): How many times to difference
  - `q` (MA order, 0-5): Past errors used
- **Key metric:** MAE, RMSE
- **Note:** Set `d > 0` if data is non-stationary

### SARIMA
**Description:** Seasonal ARIMA. Handles seasonal patterns.
- **Best for:** Seasonal time series (monthly, quarterly, yearly patterns)
- **Complexity:** Medium-High
- **Key parameters:**
  - `p, d, q`: Same as ARIMA
  - `P, D, Q`: Seasonal components
  - `m`: Seasonal period (12 for monthly, 4 for quarterly)
- **Key metric:** MAE, RMSE

### Exponential Smoothing
**Description:** Weighted average of past observations. Fast and interpretable.
- **Best for:** Trend/seasonal data, forecasting, real-time systems
- **Complexity:** Low
- **Key parameters:**
  - `trend` (add, mul, None)
  - `seasonal` (add, mul, None)
  - `seasonal_periods` (typically 12 or 52)
- **Key metric:** MAE, RMSE

---

## Clustering Models (3 total)

### K-Means
**Description:** Partitions data into k clusters based on centroids.
- **Best for:** Quick clustering, round clusters, exploratory analysis
- **Complexity:** Low-Medium
- **Key parameters:**
  - `n_clusters` (2-15): Number of clusters to create
  - `init` (kmeans++, random): Initialization method
  - `max_iter` (100-500): Iterations before stopping
- **Key metric:** Silhouette Score (higher is better), Inertia
- **Note:** Run multiple times (random initialization)

### DBSCAN
**Description:** Density-based clustering. Finds arbitrary-shaped clusters.
- **Best for:** Non-convex clusters, outlier detection
- **Complexity:** Medium
- **Key parameters:**
  - `eps` (0.1-1.0): Maximum distance between neighbors
  - `min_samples` (2-10): Minimum points to form a cluster
- **Key metric:** Silhouette Score
- **Warning:** Sensitive to parameter tuning

### Hierarchical Clustering
**Description:** Builds a dendrogram. Bottom-up or top-down approach.
- **Best for:** Exploring cluster hierarchy, dendrogram visualization
- **Complexity:** Medium
- **Key parameters:**
  - `n_clusters` (2-15): Number of final clusters
  - `linkage` (ward, complete, average, single)
- **Key metric:** Silhouette Score

---

## Deep Learning Models (4 total, optional TensorFlow)

### Multi-Layer Perceptron (MLP)
**Description:** Fully connected neural network. Universal function approximator.
- **Best for:** Any tabular data task, structured data
- **Complexity:** Medium-High
- **Key parameters:**
  - `units` (16-256): Neurons per hidden layer
  - `layers` (1-4): Number of hidden layers
  - `dropout` (0-0.5): Regularization to prevent overfitting
  - `activation` (relu, sigmoid, tanh)
  - `optimizer` (adam, sgd, rmsprop)
  - `learning_rate` (0.0001-0.1, log scale)
  - `epochs` (10-200)
  - `batch_size` (16, 32, 64, 128, 256)
- **Key metric:** Accuracy (classification) / R² (regression)

### LSTM (Long Short-Term Memory)
**Description:** Recurrent neural network for sequences. Remembers long-term patterns.
- **Best for:** Time series, text, sequential data
- **Complexity:** High
- **Key parameters:**
  - All MLP parameters plus:
  - `bidirectional` (bool): Process forwards AND backwards
  - `return_sequences` (bool): Output full sequence or just final step
  - `stateful` (bool): Carry hidden state across batches
- **Key metric:** RMSE (time series) / Accuracy (classification)
- **Best practice:** Start with bidirectional=True

### CNN-1D (1D Convolutional Neural Network)
**Description:** Learns local patterns in sequences.
- **Best for:** Time series, signal processing, feature extraction
- **Complexity:** High
- **Key parameters:**
  - All MLP parameters plus:
  - `units` (filters per layer)
  - `kernel_size` (3-7): Window size for convolution
- **Key metric:** RMSE (time series) / Accuracy (classification)

### Autoencoder
**Description:** Unsupervised learning. Learns compressed representation (embedding).
- **Best for:** Dimensionality reduction, anomaly detection, feature learning
- **Complexity:** Very High
- **Key parameters:**
  - `units` (bottleneck dimension)
  - `layers` (depth)
  - `dropout` (regularization)
  - `activation` (relu, sigmoid, tanh)
- **Key metric:** Reconstruction loss

---

## Quick Decision Guide

### I have a regression problem
1. **Start with:** Random Forest Regressor or XGBoost Regressor
2. **If interpretability matters:** Linear Regression or Ridge
3. **If data is small:** SVR or Ridge
4. **If data is large:** XGBoost Regressor

### I have a classification problem
1. **Start with:** XGBoost Classifier or Random Forest Classifier
2. **If interpretability matters:** Logistic Regression
3. **If data is imbalanced:** XGBoost with `scale_pos_weight`
4. **For real-time:** Naive Bayes

### I have time series data
1. **Start with:** ARIMA or Exponential Smoothing
2. **If seasonal:** SARIMA
3. **If non-linear patterns:** LSTM
4. **For fast forecasting:** Exponential Smoothing

### I need to cluster data
1. **Start with:** K-Means (quick baseline)
2. **If clusters are irregular:** DBSCAN
3. **If you need a hierarchy:** Hierarchical Clustering
4. **For many features:** Use PCA first

### I want a deep learning model
1. **Required:** TensorFlow installed
2. **General tabular data:** MLP
3. **Time series:** LSTM (bidirectional recommended)
4. **Signal/feature learning:** CNN-1D
5. **Anomaly detection:** Autoencoder

---

## Parameter Quick Reference

| Model | Typical Best Hyperparameters |
|-------|------------------------------|
| XGBoost | lr=0.1, n_est=100-300, depth=5-7 |
| Random Forest | n_est=100-200, depth=10-15 |
| Logistic Reg | C=1.0, max_iter=1000 |
| SVM | C=1.0, kernel=rbf |
| KNN | k=5, weights='distance' |
| ARIMA | p=1, d=1, q=1 (start point) |
| LSTM | units=64-128, dropout=0.2, lr=0.001 |
| K-Means | k=sqrt(n_samples), init='kmeans++' |

