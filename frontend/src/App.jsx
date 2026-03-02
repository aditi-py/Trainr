import React, {
  useState,
  useReducer,
  useCallback,
  useRef,
  useEffect,
  useMemo,
} from 'react';
import { createPortal } from 'react-dom';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

// ─────────────────────────────────────────────
// GLOBAL STYLES (injected once)
// ─────────────────────────────────────────────
const GlobalStyles = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'DM Sans', sans-serif; background: #060611; overflow-x: hidden; }
    body::after {
      content: ''; position: fixed; inset: 0;
      background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,213,0.012) 2px, rgba(0,255,213,0.012) 4px);
      pointer-events: none; z-index: 9997;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a1a; }
    ::-webkit-scrollbar-thumb { background: #00ffd5; border-radius: 3px; }
    input[type=range] { accent-color: #00ffd5; cursor: pointer; }
    input[type=checkbox] { accent-color: #00ffd5; cursor: pointer; width: 16px; height: 16px; }
    select, input[type=number], input[type=text] { font-family: 'DM Sans', sans-serif; outline: none; }
    select:focus, input[type=number]:focus, input[type=text]:focus {
      border-color: #00ffd5 !important;
      box-shadow: 0 0 0 2px rgba(0,255,213,0.15), 0 0 8px rgba(0,255,213,0.25) !important;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    @keyframes slideIn { from{transform:translateX(120%);opacity:0} to{transform:translateX(0);opacity:1} }
    @keyframes spin { to{transform:rotate(360deg)} }
    @keyframes neonPulse {
      0%,100%{ box-shadow: 0 0 4px #00ffd5, 0 0 10px #00ffd5; }
      50%    { box-shadow: 0 0 8px #00ffd5, 0 0 24px #00ffd5, 0 0 40px rgba(0,255,213,0.3); }
    }
    @keyframes cornerBlink { 0%,88%,100%{opacity:1} 93%{opacity:0.2} }
    @keyframes glitch1 {
      0%,100%{clip-path:inset(40% 0 61% 0);transform:skew(0.1deg)}
      25%{clip-path:inset(92% 0 1% 0);transform:skew(0.4deg)}
      50%{clip-path:inset(25% 0 58% 0);transform:skew(-0.2deg)}
      75%{clip-path:inset(54% 0 7% 0);transform:skew(0.15deg)}
    }
    @keyframes glitch2 {
      0%,100%{clip-path:inset(54% 0 7% 0);transform:skew(-0.1deg)}
      25%{clip-path:inset(25% 0 58% 0);transform:skew(0.3deg)}
      50%{clip-path:inset(40% 0 61% 0);transform:skew(-0.4deg)}
      75%{clip-path:inset(92% 0 1% 0);transform:skew(0.2deg)}
    }
    @keyframes scanMove { 0%{top:-4px} 100%{top:calc(100% + 4px)} }
    @keyframes floatY { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
    .skeleton { animation: pulse 1.5s ease-in-out infinite; background: #1e1e4a !important; }
    .glitch-logo {
      position: relative; display: inline-block;
      font-family: 'Orbitron', sans-serif; font-weight: 900;
      color: #00ffd5; letter-spacing: 2px;
      text-shadow: 0 0 10px #00ffd5, 0 0 20px rgba(0,255,213,0.5);
    }
    .glitch-logo::before,.glitch-logo::after {
      content: attr(data-text); position: absolute; top: 0; left: 0;
      width: 100%; height: 100%; opacity: 0.7;
    }
    .glitch-logo::before { color: #ff006e; animation: glitch1 5s infinite 0.5s; }
    .glitch-logo::after  { color: #4361ee; animation: glitch2 5s infinite 1s; }
    .neon-card { position: relative; overflow: hidden; }
    .neon-card::before {
      content: ''; position: absolute; top: -4px; left: 0; right: 0; height: 2px;
      background: linear-gradient(90deg, transparent, #00ffd5, transparent);
      animation: scanMove 4s linear infinite; opacity: 0.3; pointer-events: none;
    }
  `}</style>
);

// ─────────────────────────────────────────────
// DESIGN TOKENS
// ─────────────────────────────────────────────
const tok = (dark) => ({
  bg:       dark ? '#060611' : '#f0f4f8',
  card:     dark ? '#0a0a1a' : '#ffffff',
  border:   dark ? '#1a1a3e' : '#e2e8f0',
  text:     dark ? '#c0c8ff' : '#0f172a',
  muted:    dark ? '#5565a0' : '#64748b',
  accent:   '#00ffd5',
  violet:   '#ff006e',
  shadow:   dark ? '0 2px 12px rgba(0,255,213,0.06)' : '0 1px 3px rgba(0,0,0,0.12)',
  radius:   '4px',
  trans:    'all 150ms ease',
  inputBg:  dark ? '#080816' : '#f8fafc',
  neonGlow: '0 0 8px #00ffd5, 0 0 16px rgba(0,255,213,0.3)',
  magentaGlow: '0 0 8px #ff006e, 0 0 16px rgba(255,0,110,0.3)',
});

// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
const initialState = {
  data:     { fileId: null, fileName: '', columns: [], types: {}, preview: [], shape: {} },
  model:    { category: '', id: '', name: '', taskType: '' },
  features: { inputs: [], target: '', dateColumn: '' },
  params:   {},
  split:    { testSize: 0.2, cvFolds: 5, useCv: false },
  results:  { current: null, comparison: [] },
  ui:       { step: 1, darkMode: true, loading: false, error: null, healthOk: true, sidebarOpen: true },
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_DATA':     return { ...state, data: { ...state.data, ...action.payload } };
    case 'SET_MODEL':    return { ...state, model: { ...state.model, ...action.payload } };
    case 'SET_FEATURES': return { ...state, features: { ...state.features, ...action.payload } };
    case 'SET_PARAMS':   return { ...state, params: { ...state.params, ...action.payload } };
    case 'SET_SPLIT':    return { ...state, split: { ...state.split, ...action.payload } };
    case 'SET_RESULTS':  return { ...state, results: { ...state.results, ...action.payload } };
    case 'SET_UI':       return { ...state, ui: { ...state.ui, ...action.payload } };
    case 'RESET_PARAMS': return { ...state, params: action.payload };
    default:             return state;
  }
}

// ─────────────────────────────────────────────
// MODEL CATALOG
// ─────────────────────────────────────────────
const MODEL_CATALOG = {
  Regression: [
    { id: 'linear_regression',           name: 'Linear Regression',             complexity: 'Low',  taskType: 'regression',      desc: 'Fits a linear relationship between features and target. Fast and interpretable.', bestUse: 'Baseline regression, linearly separable data.' },
    { id: 'ridge',                        name: 'Ridge Regression',              complexity: 'Low',  taskType: 'regression',      desc: 'Linear regression with L2 regularization to prevent overfitting.', bestUse: 'High-dimensional data with multicollinearity.' },
    { id: 'lasso',                        name: 'Lasso Regression',              complexity: 'Low',  taskType: 'regression',      desc: 'Linear regression with L1 regularization; performs feature selection.', bestUse: 'Sparse models where few features matter.' },
    { id: 'random_forest_regressor',      name: 'Random Forest Regressor',       complexity: 'Med',  taskType: 'regression',      desc: 'Ensemble of decision trees averaged for robust predictions.', bestUse: 'Non-linear tabular data, mixed feature types.' },
    { id: 'xgboost_regressor',            name: 'XGBoost Regressor',             complexity: 'Med',  taskType: 'regression',      desc: 'Gradient-boosted trees with regularization. State-of-the-art for tabular data.', bestUse: 'Kaggle-style tabular regression tasks.' },
    { id: 'gradient_boosting_regressor',  name: 'Gradient Boosting Regressor',   complexity: 'Med',  taskType: 'regression',      desc: 'Sequentially builds trees to correct errors. Highly accurate.', bestUse: 'Medium-sized datasets, structured data.' },
    { id: 'svr',                          name: 'Support Vector Regressor',      complexity: 'Med',  taskType: 'regression',      desc: 'Finds a hyperplane that fits most data within a margin.', bestUse: 'Small to medium datasets, high-dimensional spaces.' },
  ],
  Classification: [
    { id: 'logistic_regression',          name: 'Logistic Regression',           complexity: 'Low',  taskType: 'classification',  desc: 'Probabilistic linear classifier. Fast, interpretable baseline.', bestUse: 'Binary classification, linearly separable classes.' },
    { id: 'random_forest_classifier',     name: 'Random Forest Classifier',      complexity: 'Med',  taskType: 'classification',  desc: 'Ensemble of decision trees voted to classify samples.', bestUse: 'General-purpose classification with mixed features.' },
    { id: 'xgboost_classifier',           name: 'XGBoost Classifier',            complexity: 'Med',  taskType: 'classification',  desc: 'Boosted trees with built-in regularization. Top performer on tabular data.', bestUse: 'Binary and multi-class classification.' },
    { id: 'svm_classifier',               name: 'SVM Classifier',                complexity: 'Med',  taskType: 'classification',  desc: 'Finds maximum-margin hyperplane to separate classes.', bestUse: 'Text classification, high-dimensional data.' },
    { id: 'knn',                          name: 'K-Nearest Neighbors',           complexity: 'Low',  taskType: 'classification',  desc: 'Classifies based on majority vote of nearest neighbors.', bestUse: 'Small datasets, local pattern recognition.' },
    { id: 'naive_bayes',                  name: 'Naive Bayes',                   complexity: 'Low',  taskType: 'classification',  desc: 'Probabilistic classifier using Bayes theorem with independence assumption.', bestUse: 'Text classification, spam detection.' },
    { id: 'gradient_boosting_classifier', name: 'Gradient Boosting Classifier',  complexity: 'Med',  taskType: 'classification',  desc: 'Builds trees sequentially to minimize classification error.', bestUse: 'Structured data classification with high accuracy needs.' },
  ],
  Statistical: [
    { id: 'arima',                  name: 'ARIMA',                      complexity: 'Med',  taskType: 'timeseries',      desc: 'Autoregressive Integrated Moving Average for univariate time series.', bestUse: 'Stationary or differenced time series forecasting.' },
    { id: 'sarima',                 name: 'SARIMA',                     complexity: 'High', taskType: 'timeseries',      desc: 'Seasonal ARIMA that captures periodic patterns in time series.', bestUse: 'Seasonal data like sales, weather, economics.' },
    { id: 'exponential_smoothing',  name: 'Exponential Smoothing',      complexity: 'Low',  taskType: 'timeseries',      desc: 'Weighted averages of past observations with exponential decay.', bestUse: 'Short-term forecasting with trend and seasonality.' },
  ],
  Clustering: [
    { id: 'kmeans',       name: 'K-Means',              complexity: 'Low',  taskType: 'clustering',      desc: 'Partitions data into K clusters by minimizing within-cluster variance.', bestUse: 'Customer segmentation, document clustering.' },
    { id: 'dbscan',       name: 'DBSCAN',                complexity: 'Med',  taskType: 'clustering',      desc: 'Density-based clustering that finds arbitrarily shaped clusters and outliers.', bestUse: 'Geospatial data, anomaly detection.' },
    { id: 'hierarchical', name: 'Hierarchical Clustering', complexity: 'Med', taskType: 'clustering',     desc: 'Builds a tree of clusters using agglomerative or divisive methods.', bestUse: 'Gene expression, document hierarchies.' },
  ],
  'Deep Learning': [
    { id: 'mlp',         name: 'MLP',          complexity: 'High', taskType: 'deep_learning', desc: 'Multi-layer perceptron — a fully connected feedforward neural network.', bestUse: 'Tabular data, general-purpose deep learning.' },
    { id: 'lstm',        name: 'LSTM',         complexity: 'High', taskType: 'deep_learning', desc: 'Long Short-Term Memory network for sequential and time-series data.', bestUse: 'Time series forecasting, NLP sequences.' },
    { id: 'cnn_1d',      name: 'CNN 1D',       complexity: 'High', taskType: 'deep_learning', desc: '1D Convolutional network for local pattern extraction from sequences.', bestUse: 'Signal processing, time-series classification.' },
    { id: 'autoencoder', name: 'Autoencoder',  complexity: 'High', taskType: 'deep_learning', desc: 'Encoder-decoder network for unsupervised feature learning and anomaly detection.', bestUse: 'Dimensionality reduction, anomaly detection.' },
  ],
};

const COMPLEXITY_COLOR = { Low: '#39ff14', Med: '#ffbe0b', High: '#ff006e' };

// ─────────────────────────────────────────────
// DEFAULT PARAMS PER MODEL
// ─────────────────────────────────────────────
function defaultParams(modelId) {
  const map = {
    random_forest_regressor:      { n_estimators: 100, max_depth: 10, min_samples_split: 2 },
    random_forest_classifier:     { n_estimators: 100, max_depth: 10, min_samples_split: 2 },
    xgboost_regressor:            { learning_rate: 0.1, n_estimators: 100, max_depth: 5, subsample: 0.8, colsample_bytree: 0.8 },
    xgboost_classifier:           { learning_rate: 0.1, n_estimators: 100, max_depth: 5, subsample: 0.8, colsample_bytree: 0.8 },
    logistic_regression:          { C: 1.0, max_iter: 200, solver: 'lbfgs' },
    arima:                        { p: 1, d: 1, q: 1 },
    sarima:                       { p: 1, d: 1, q: 1, P: 1, D: 1, Q: 1, m: 12 },
    kmeans:                       { n_clusters: 4, init: 'k-means++', max_iter: 300 },
    svm_classifier:               { C: 1.0, kernel: 'rbf', gamma: 'scale' },
    svr:                          { C: 1.0, kernel: 'rbf', gamma: 'scale' },
    knn:                          { n_neighbors: 5 },
    ridge:                        { alpha: 1.0 },
    lasso:                        { alpha: 1.0 },
    dbscan:                       { eps: 0.5, min_samples: 5 },
    hierarchical:                 { n_clusters: 4, linkage: 'ward' },
    exponential_smoothing:        { trend: 'add', seasonal: 'add', seasonal_periods: 12 },
    gradient_boosting_regressor:  { learning_rate: 0.1, n_estimators: 100, max_depth: 3 },
    gradient_boosting_classifier: { learning_rate: 0.1, n_estimators: 100, max_depth: 3 },
    naive_bayes:                  {},
    linear_regression:            {},
    mlp:         { units: 64, layers: 2, dropout: 0.2, activation: 'relu', weight_init: 'glorot_uniform', optimizer: 'adam', learning_rate: 0.001, lr_scheduler: 'none', loss: 'mse', epochs: 50, batch_size: 32, validation_split: 0.1, reg_type: 'none', reg_lambda: 0.001, early_stopping: false, patience: 10 },
    lstm:        { units: 64, layers: 2, dropout: 0.2, activation: 'tanh', weight_init: 'glorot_uniform', optimizer: 'adam', learning_rate: 0.001, lr_scheduler: 'none', loss: 'mse', epochs: 50, batch_size: 32, validation_split: 0.1, reg_type: 'none', reg_lambda: 0.001, early_stopping: false, patience: 10, bidirectional: false, return_sequences: false, stateful: false },
    cnn_1d:      { units: 64, layers: 2, dropout: 0.2, activation: 'relu', weight_init: 'glorot_uniform', optimizer: 'adam', learning_rate: 0.001, lr_scheduler: 'none', loss: 'mse', epochs: 50, batch_size: 32, validation_split: 0.1, reg_type: 'none', reg_lambda: 0.001, early_stopping: false, patience: 10 },
    autoencoder: { units: 64, layers: 2, dropout: 0.2, activation: 'relu', weight_init: 'glorot_uniform', optimizer: 'adam', learning_rate: 0.001, lr_scheduler: 'none', loss: 'mse', epochs: 50, batch_size: 32, validation_split: 0.1, reg_type: 'none', reg_lambda: 0.001, early_stopping: false, patience: 10 },
  };
  return map[modelId] || {};
}

const PRESETS = {
  conservative: (modelId) => {
    const d = defaultParams(modelId);
    if (['mlp','lstm','cnn_1d','autoencoder'].includes(modelId)) return { ...d, learning_rate: 0.0001, epochs: 20, dropout: 0.3, reg_type: 'l2', reg_lambda: 0.01 };
    if (modelId.includes('xgboost')) return { ...d, learning_rate: 0.01, n_estimators: 50, max_depth: 3 };
    if (modelId.includes('random_forest')) return { ...d, n_estimators: 50, max_depth: 5 };
    return d;
  },
  balanced: (modelId) => defaultParams(modelId),
  aggressive: (modelId) => {
    const d = defaultParams(modelId);
    if (['mlp','lstm','cnn_1d','autoencoder'].includes(modelId)) return { ...d, learning_rate: 0.01, epochs: 200, dropout: 0.1, units: 256, layers: 4 };
    if (modelId.includes('xgboost')) return { ...d, learning_rate: 0.3, n_estimators: 500, max_depth: 10 };
    if (modelId.includes('random_forest')) return { ...d, n_estimators: 500, max_depth: 30 };
    return d;
  },
};

// ─────────────────────────────────────────────
// TOAST SYSTEM
// ─────────────────────────────────────────────
const ToastContext = React.createContext(null);

function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const dismiss = useCallback((id) => {
    setToasts(t => t.filter(x => x.id !== id));
  }, []);
  const addToast = useCallback((msg, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, msg, type }]);
    // Errors stay until manually dismissed; others auto-dismiss after 4s
    if (type !== 'error') {
      setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
    }
  }, []);
  return (
    <ToastContext.Provider value={addToast}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

function ToastContainer({ toasts, onDismiss }) {
  const COLOR = { success: '#39ff14', error: '#ff006e', info: '#00ffd5' };
  return (
    <div style={{
      position: 'fixed', top: 68, right: 20, zIndex: 9999,
      display: 'flex', flexDirection: 'column', gap: 8,
      maxWidth: 360, width: 'calc(100vw - 40px)',
    }}>
      {toasts.map(t => (
        <div key={t.id} style={{
          display: 'flex', alignItems: 'flex-start', gap: 10,
          background: '#0a0a1a', color: '#c0c8ff',
          border: `1px solid ${COLOR[t.type]}44`,
          borderLeft: `3px solid ${COLOR[t.type]}`,
          borderRadius: 4, padding: '12px 14px',
          fontSize: 13, fontFamily: 'DM Sans, sans-serif',
          boxShadow: `0 4px 24px rgba(0,0,0,0.6), 0 0 12px ${COLOR[t.type]}22`,
          animation: 'slideIn 200ms ease',
          wordBreak: 'break-word',
        }}>
          <span style={{ color: COLOR[t.type], fontSize: 16, flexShrink: 0, marginTop: 1, textShadow: `0 0 6px ${COLOR[t.type]}` }}>
            {t.type === 'success' ? <CyberIcon name="check" size={15} color={COLOR[t.type]} /> : t.type === 'error' ? <CyberIcon name="close" size={15} color={COLOR[t.type]} /> : <CyberIcon name="info" size={15} color={COLOR[t.type]} />}
          </span>
          <span style={{ flex: 1, lineHeight: 1.5 }}>{t.msg}</span>
          <button onClick={() => onDismiss(t.id)} style={{
            background: 'none', border: 'none', color: '#5565a0',
            cursor: 'pointer', padding: '0 0 0 4px',
            flexShrink: 0, display: 'flex', alignItems: 'center',
          }}><CyberIcon name="close" size={13} color="#5565a0" /></button>
        </div>
      ))}
    </div>
  );
}

function useToast() { return React.useContext(ToastContext); }

// ─────────────────────────────────────────────
// CYBERPUNK BACKGROUND — matrix rain canvas
// ─────────────────────────────────────────────
function CyberpunkBackground() {
  const canvasRef = useRef();
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize();
    window.addEventListener('resize', resize);
    const chars = 'アイウエオカキクケコ0123456789ABCDEF'.split('');
    const cols = Math.floor(canvas.width / 28);
    const drops = Array(cols).fill(0).map(() => Math.random() * -80);
    let animId, last = 0;
    const FPS = 6; // very slow, ambient pace
    const draw = (ts) => {
      animId = requestAnimationFrame(draw);
      if (ts - last < 1000 / FPS) return;
      last = ts;
      ctx.fillStyle = 'rgba(6,6,17,0.20)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      drops.forEach((y, i) => {
        const bright = Math.random() > 0.96;
        ctx.fillStyle = bright ? '#c0fff5' : '#00ffd5';
        ctx.font = `12px "Share Tech Mono", monospace`;
        ctx.globalAlpha = bright ? 0.4 : 0.07 + Math.random() * 0.06;
        ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * 28, y * 20);
        ctx.globalAlpha = 1;
        if (y * 20 > canvas.height && Math.random() > 0.97) drops[i] = 0;
        drops[i] += 0.2;
      });
    };
    animId = requestAnimationFrame(draw);
    return () => { window.removeEventListener('resize', resize); cancelAnimationFrame(animId); };
  }, []);
  return <canvas ref={canvasRef} style={{ position: 'fixed', top: 0, left: 0, zIndex: 0, pointerEvents: 'none' }} />;
}

// Animated L-bracket corner decorations
function CyberpunkCorners() {
  const SZ = 48, T = 2, C = '#00ffd5';
  const corner = (top, left, flipH, flipV) => (
    <div style={{
      position: 'fixed',
      top: top ? 12 : 'auto', bottom: top ? 'auto' : 12,
      left: left ? 12 : 'auto', right: left ? 'auto' : 12,
      width: SZ, height: SZ, zIndex: 9998, pointerEvents: 'none',
      animation: 'cornerBlink 5s infinite',
      animationDelay: `${(flipH ? 1 : 0) + (flipV ? 2 : 0)}s`,
    }}>
      <svg width={SZ} height={SZ} style={{ transform: `scale(${flipH?-1:1},${flipV?-1:1})`, display:'block' }}>
        <line x1="0" y1={T/2} x2={SZ} y2={T/2} stroke={C} strokeWidth={T} />
        <line x1={T/2} y1="0" x2={T/2} y2={SZ} stroke={C} strokeWidth={T} />
        <circle cx="8" cy="8" r="2" fill={C} opacity="0.6" />
      </svg>
    </div>
  );
  return <>
    {corner(true,  true,  false, false)}
    {corner(true,  false, true,  false)}
    {corner(false, true,  false, true)}
    {corner(false, false, true,  true)}
  </>;
}

// ─────────────────────────────────────────────
// CYBERPUNK SVG ICONS
// ─────────────────────────────────────────────
function CyberIcon({ name, size = 16, color = 'currentColor' }) {
  const s = { width: size, height: size, display: 'inline-block', verticalAlign: 'middle', flexShrink: 0 };
  const p = { fill: 'none', xmlns: 'http://www.w3.org/2000/svg' };
  if (name === 'upload') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M1 12v3h14v-3" stroke={color} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M8 1v9M5 4l3-3 3 3" stroke={color} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
  if (name === 'cpu') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <rect x="4" y="4" width="8" height="8" stroke={color} strokeWidth="1.2"/>
      <path d="M4 6H1M4 10H1M12 6h3M12 10h3M6 4V1M10 4V1M6 12v3M10 12v3" stroke={color} strokeWidth="1.2" strokeLinecap="round"/>
      <rect x="6.5" y="6.5" width="3" height="3" fill={color} fillOpacity="0.4"/>
    </svg>
  );
  if (name === 'hex') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M8 1.5L13.5 4.75V11.25L8 14.5L2.5 11.25V4.75z" stroke={color} strokeWidth="1.2"/>
      <circle cx="8" cy="8" r="2.5" stroke={color} strokeWidth="1.2"/>
    </svg>
  );
  if (name === 'sliders') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M1 4h14M1 9h14M1 13h14" stroke={color} strokeWidth="1.2" strokeLinecap="round"/>
      <circle cx="5" cy="4" r="1.8" fill={color}/>
      <circle cx="11" cy="9" r="1.8" fill={color}/>
      <circle cx="4" cy="13" r="1.8" fill={color}/>
    </svg>
  );
  if (name === 'chart') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M1 14.5h14" stroke={color} strokeWidth="1.2" strokeLinecap="round"/>
      <rect x="2" y="9" width="3" height="5.5" stroke={color} strokeWidth="1.2"/>
      <rect x="6.5" y="5" width="3" height="9.5" stroke={color} strokeWidth="1.2"/>
      <rect x="11" y="2" width="3" height="12.5" stroke={color} strokeWidth="1.2"/>
    </svg>
  );
  if (name === 'warn') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M8 2L14.5 14H1.5z" stroke={color} strokeWidth="1.2" strokeLinejoin="round"/>
      <path d="M8 7v3" stroke={color} strokeWidth="1.2" strokeLinecap="round"/>
      <circle cx="8" cy="11.5" r="0.7" fill={color}/>
    </svg>
  );
  if (name === 'close') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M3 3l10 10M13 3L3 13" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
  if (name === 'check') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <path d="M2 8l4 4 8-8" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
  if (name === 'info') return (
    <svg style={s} viewBox="0 0 16 16" {...p}>
      <circle cx="8" cy="8" r="6.5" stroke={color} strokeWidth="1.2"/>
      <path d="M8 7v4" stroke={color} strokeWidth="1.2" strokeLinecap="round"/>
      <circle cx="8" cy="5" r="0.7" fill={color}/>
    </svg>
  );
  return null;
}

// ─────────────────────────────────────────────
// SMALL UI PRIMITIVES
// ─────────────────────────────────────────────
function Spinner({ size = 18, color = '#00ffd5' }) {
  return (
    <span style={{
      display: 'inline-block', width: size, height: size,
      border: `2px solid ${color}22`,
      borderTop: `2px solid ${color}`,
      borderRadius: '50%',
      animation: 'spin 600ms linear infinite',
      flexShrink: 0,
      boxShadow: `0 0 6px ${color}`,
    }} />
  );
}

function Badge({ children, color = '#00ffd5', bg }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      padding: '2px 8px', borderRadius: 2,
      fontSize: 11, fontWeight: 600, letterSpacing: 0.5,
      color: color,
      background: bg || `${color}12`,
      border: `1px solid ${color}44`,
      whiteSpace: 'nowrap',
      fontFamily: 'Share Tech Mono, DM Mono, monospace',
      textShadow: `0 0 4px ${color}88`,
    }}>
      {children}
    </span>
  );
}

function HelpTip({ text }) {
  const [pos, setPos] = useState(null);
  const btnRef = useRef();

  const handleEnter = () => {
    if (!btnRef.current) return;
    const r = btnRef.current.getBoundingClientRect();
    // prefer showing above; if too close to top, show below
    const above = r.top > 120;
    setPos({
      left: Math.min(r.left + r.width / 2, window.innerWidth - 130),
      top: above ? r.top - 8 : r.bottom + 8,
      above,
    });
  };

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center' }}
      onMouseEnter={handleEnter} onMouseLeave={() => setPos(null)}>
      <span ref={btnRef} style={{
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        width: 16, height: 16, borderRadius: '50%',
        background: '#00ffd515', color: '#00ffd5',
        border: '1px solid #00ffd555',
        fontSize: 10, cursor: 'help', fontWeight: 700, userSelect: 'none',
        flexShrink: 0,
      }}>?</span>
      {pos && createPortal(
        <div style={{
          position: 'fixed',
          left: pos.left,
          top: pos.above ? pos.top - 4 : pos.top + 4,
          transform: pos.above ? 'translate(-50%, -100%)' : 'translate(-50%, 0)',
          background: '#08081a',
          color: '#c0c8ff',
          border: '1px solid #00ffd544',
          borderRadius: 4,
          padding: '8px 12px',
          fontSize: 12,
          lineHeight: 1.65,
          width: 220,
          zIndex: 99999,
          boxShadow: '0 8px 32px rgba(0,0,0,0.9), 0 0 16px rgba(0,255,213,0.12)',
          pointerEvents: 'none',
          whiteSpace: 'normal',
          fontFamily: 'DM Sans, sans-serif',
        }}>
          {text}
        </div>,
        document.body
      )}
    </span>
  );
}

function Skeleton({ w = '100%', h = 20, r = 6 }) {
  return <div className="skeleton" style={{ width: w, height: h, borderRadius: r, background: '#334155' }} />;
}

function Card({ children, style, dark, neon }) {
  const t = tok(dark ?? true);
  return (
    <div className={neon !== false ? 'neon-card' : ''} style={{
      background: t.card,
      border: `1px solid ${t.border}`,
      borderRadius: t.radius, padding: 20,
      boxShadow: dark !== false ? `${t.shadow}, inset 0 0 30px rgba(0,0,0,0.3)` : t.shadow,
      transition: t.trans,
      ...style,
    }}>
      {children}
    </div>
  );
}

function Button({ children, onClick, disabled, variant = 'primary', dark, style: extraStyle, size = 'md' }) {
  const [hover, setHover] = useState(false);
  const t = tok(dark ?? true);
  const pad = size === 'sm' ? '6px 14px' : size === 'lg' ? '14px 28px' : '10px 20px';
  const fs  = size === 'sm' ? 12 : size === 'lg' ? 15 : 13;

  const base = {
    display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
    padding: pad, borderRadius: 2, fontFamily: 'DM Sans, sans-serif',
    fontWeight: 700, fontSize: fs, cursor: disabled ? 'not-allowed' : 'pointer',
    border: 'none', transition: t.trans, opacity: disabled ? 0.4 : 1,
    letterSpacing: '0.5px', textTransform: 'uppercase',
    ...extraStyle,
  };
  const styles = {
    primary: {
      ...base, background: hover && !disabled ? 'rgba(0,255,213,0.1)' : 'transparent',
      color: '#00ffd5', border: '1px solid #00ffd5',
      boxShadow: hover && !disabled ? '0 0 12px rgba(0,255,213,0.5), inset 0 0 8px rgba(0,255,213,0.05)' : '0 0 4px rgba(0,255,213,0.2)',
      textShadow: '0 0 6px rgba(0,255,213,0.8)',
    },
    secondary: {
      ...base, background: hover && !disabled ? 'rgba(0,255,213,0.05)' : 'transparent',
      color: t.text, border: `1px solid ${t.border}`,
    },
    danger: {
      ...base, background: hover && !disabled ? 'rgba(255,0,110,0.1)' : 'transparent',
      color: '#ff006e', border: '1px solid #ff006e44',
      boxShadow: hover && !disabled ? '0 0 10px rgba(255,0,110,0.4)' : 'none',
    },
    ghost: {
      ...base, background: hover && !disabled ? 'rgba(0,255,213,0.05)' : 'transparent',
      color: t.muted, border: '1px solid transparent',
    },
  };
  return (
    <button style={styles[variant]} onClick={disabled ? undefined : onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}>
      {children}
    </button>
  );
}

// ─────────────────────────────────────────────
// STEP 1 — IMPORT DATA
// ─────────────────────────────────────────────
const TYPE_META = {
  numeric:     { label: 'Numeric',     icon: '🔢', color: '#3b82f6' },
  categorical: { label: 'Categorical', icon: '🔤', color: '#a855f7' },
  datetime:    { label: 'Datetime',    icon: '📅', color: '#f97316' },
  text:        { label: 'Text',        icon: '📝', color: '#64748b' },
};

function StepImport({ state, dispatch }) {
  const { data, ui } = state;
  const dark = ui.darkMode;
  const t = tok(dark);
  const toast = useToast();
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef();

  const FORMATS = ['CSV', 'Excel', 'Parquet', 'JSON', 'TXT'];
  const FORMAT_ACCEPTS = {
    CSV:     '.csv',
    Excel:   '.xlsx,.xls',
    Parquet: '.parquet',
    JSON:    '.json',
    TXT:     '.txt',
  };

  const openForFormat = (fmt) => {
    fileRef.current.accept = FORMAT_ACCEPTS[fmt];
    fileRef.current.value  = '';   // allow re-selecting same file
    fileRef.current.click();
  };

  const handleFile = async (file) => {
    if (!file) return;
    setUploading(true);
    dispatch({ type: 'SET_UI', payload: { loading: true, error: null } });
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch('http://localhost:8000/upload', { method: 'POST', body: fd });
      if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
      const json = await res.json();
      dispatch({ type: 'SET_DATA', payload: {
        fileId: json.file_id,
        fileName: file.name,
        columns: json.columns || [],
        types: json.inferred_types || {},
        preview: json.preview || [],
        shape: json.shape || {},
      }});
      toast('File uploaded successfully!', 'success');
    } catch (err) {
      dispatch({ type: 'SET_UI', payload: { error: err.message } });
      toast(err.message, 'error');
    } finally {
      setUploading(false);
      dispatch({ type: 'SET_UI', payload: { loading: false } });
    }
  };

  const onDrop = (e) => {
    e.preventDefault(); setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: t.text, marginBottom: 6 }}>Import Data</h2>
        <p style={{ color: t.muted, fontSize: 14 }}>Upload your dataset to get started. Supports multiple formats.</p>
      </div>

      {/* Drop Zone — drag & drop only */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        style={{
          border: `1px dashed ${dragging ? '#00ffd5' : '#00ffd533'}`,
          borderRadius: 4, padding: '40px 32px',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16,
          cursor: 'default', transition: t.trans,
          background: dragging ? 'rgba(0,255,213,0.06)' : dark ? 'rgba(0,255,213,0.02)' : t.card,
          textAlign: 'center',
          boxShadow: dragging ? '0 0 24px rgba(0,255,213,0.2), inset 0 0 24px rgba(0,255,213,0.05)' : 'none',
        }}
      >
        <span style={{ color: dragging ? '#00ffd5' : '#5565a0', filter: dragging ? 'drop-shadow(0 0 8px #00ffd5)' : 'none', transition: t.trans }}>
          <CyberIcon name="upload" size={44} color={dragging ? '#00ffd5' : '#5565a0'} />
        </span>
        <div>
          <p style={{ color: t.text, fontWeight: 600, fontSize: 16, marginBottom: 4 }}>
            Drag & drop your file here
          </p>
          <p style={{ color: t.muted, fontSize: 13 }}>or click a format below to browse</p>
          <p style={{ color: t.muted, fontSize: 12, marginTop: 4 }}>Maximum file size: 500MB</p>
        </div>

        {/* Format chips — each opens a type-filtered file picker */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
          {FORMATS.map(f => (
            <span key={f}
              onClick={() => openForFormat(f)}
              style={{
                padding: '5px 14px', borderRadius: 2, fontSize: 12, fontWeight: 600,
                background: `${t.accent}18`, color: t.accent,
                border: `1px solid ${t.accent}55`,
                cursor: 'pointer', letterSpacing: '0.4px',
                fontFamily: 'Share Tech Mono, monospace',
                transition: t.trans,
                userSelect: 'none',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = `${t.accent}30`; e.currentTarget.style.boxShadow = `0 0 8px ${t.accent}44`; }}
              onMouseLeave={e => { e.currentTarget.style.background = `${t.accent}18`; e.currentTarget.style.boxShadow = 'none'; }}
            >{f}</span>
          ))}
        </div>

        <input ref={fileRef} type="file" style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])} />
      </div>

      {/* Uploading skeleton */}
      {uploading && (
        <Card dark={dark} style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <Spinner /> <span style={{ color: t.muted }}>Processing file...</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <Skeleton h={16} />
            <Skeleton h={16} w="80%" />
            <Skeleton h={16} w="60%" />
          </div>
        </Card>
      )}

      {/* Results */}
      {data.fileId && !uploading && (
        <>
          {/* File summary */}
          <Card dark={dark}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <span style={{ color: '#00ffd5', filter: 'drop-shadow(0 0 6px #00ffd5)' }}><CyberIcon name="chart" size={32} color="#00ffd5" /></span>
              <div style={{ flex: 1 }}>
                <p style={{ fontWeight: 700, fontSize: 16, color: t.text }}>{data.fileName}</p>
                <p style={{ color: t.muted, fontSize: 13, marginTop: 2 }}>
                  {(data.shape.rows || 0).toLocaleString()} rows × {data.shape.cols || data.columns.length} columns
                </p>
              </div>
              <Badge color="#22c55e">Loaded</Badge>
            </div>
          </Card>

          {/* Column cards */}
          <div>
            <h3 style={{ fontSize: 15, fontWeight: 600, color: t.text, marginBottom: 12 }}>
              Column Overview ({data.columns.length} columns)
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 10 }}>
              {data.columns.map(col => {
                const dtype = data.types[col.name] || 'text';
                const meta  = TYPE_META[dtype] || TYPE_META.text;
                const nullPct = data.shape.rows > 0 ? ((col.null_count / data.shape.rows) * 100).toFixed(1) : 0;
                const info = { nullPct, unique: col.unique_count ?? '—' };
                return (
                  <div key={col.name} style={{
                    background: t.card, border: `1px solid ${t.border}`,
                    borderRadius: 8, padding: '12px 14px',
                    borderLeft: `3px solid ${meta.color}`,
                  }}>
                    <p style={{ fontWeight: 600, fontSize: 13, color: t.text, marginBottom: 6, wordBreak: 'break-word' }}>{col.name}</p>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      <Badge color={meta.color}>{meta.icon} {meta.label}</Badge>
                    </div>
                    <p style={{ color: t.muted, fontSize: 11, marginTop: 6 }}>
                      {info.unique} unique · {info.nullPct}% null
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Preview table */}
          {data.preview.length > 0 && (
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 600, color: t.text, marginBottom: 12 }}>Data Preview (first 10 rows)</h3>
              <div style={{ overflowX: 'auto', borderRadius: 8, border: `1px solid ${t.border}` }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, fontFamily: 'DM Mono, monospace' }}>
                  <thead>
                    <tr style={{ background: dark ? '#0f172a' : '#f1f5f9' }}>
                      {data.columns.map(col => (
                        <th key={col.name} style={{
                          padding: '8px 12px', textAlign: 'left', whiteSpace: 'nowrap',
                          color: t.muted, fontWeight: 600, borderBottom: `1px solid ${t.border}`,
                        }}>{col.name}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.preview.slice(0, 10).map((row, i) => (
                      <tr key={i} style={{ background: i % 2 === 0 ? t.card : (dark ? '#162032' : '#f8fafc') }}>
                        {data.columns.map(col => (
                          <td key={col.name} style={{ padding: '7px 12px', color: t.text, borderBottom: `1px solid ${t.border}33`, whiteSpace: 'nowrap' }}>
                            {String(row[col.name] ?? '—')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
// STEP 2 — SELECT MODEL
// ─────────────────────────────────────────────
function StepModel({ state, dispatch }) {
  const { data, model, ui } = state;
  const dark = ui.darkMode;
  const t = tok(dark);
  const toast = useToast();
  const [activeTab, setActiveTab] = useState('Regression');
  const [detailModel, setDetailModel] = useState(null);

  const TABS = Object.keys(MODEL_CATALOG);

  // Recommendation logic — per-category, data-aware
  const hasDatetime = Object.values(data.types || {}).some(v => v === 'datetime');

  // Per-category best model keyed by tab name, based on dataset shape
  const recommendations = useMemo(() => {
    const rows     = data.shape?.rows || 0;
    const types    = data.types || {};
    const numCols  = Object.values(types).filter(v => v === 'numeric').length;
    const colCount = Object.keys(types).length;

    if (hasDatetime)   return { Statistical: 'arima' };
    if (numCols === 0) return { Clustering: 'kmeans' };

    let reg, cls;
    if      (rows < 500)   { reg = 'ridge';                       cls = 'logistic_regression';        }
    else if (rows < 5000)  { reg = 'random_forest_regressor';     cls = 'random_forest_classifier';   }
    else if (rows < 20000) { reg = 'gradient_boosting_regressor'; cls = 'gradient_boosting_classifier';}
    else                   { reg = 'xgboost_regressor';           cls = 'xgboost_classifier';         }

    // High-dimensional sparse data → regularised linear handles it better
    if (colCount > 30 && rows < 2000) { reg = 'lasso'; cls = 'logistic_regression'; }

    return { Regression: reg, Classification: cls, Clustering: 'kmeans' };
  }, [data.shape, data.types, hasDatetime]);

  // Single model id for the banner: use the recommended-tab's suggestion
  const recommendation = useMemo(() => (
    recommendations[recommendedTab] || Object.values(recommendations)[0] || null
  ), [recommendations, recommendedTab]);

  const recommendedTab = useMemo(() => {
    if (hasDatetime) return 'Statistical';
    const numericCols = Object.entries(data.types || {}).filter(([, v]) => v === 'numeric');
    if (numericCols.length > 0) return 'Regression';
    return 'Clustering';
  }, [data.types, hasDatetime]);

  const recModel = useMemo(() => {
    for (const [, models] of Object.entries(MODEL_CATALOG)) {
      const m = models.find(x => x.id === recommendation);
      if (m) return m;
    }
    return null;
  }, [recommendation]);

  const selectModel = (m, tab) => {
    dispatch({ type: 'SET_MODEL', payload: { id: m.id, name: m.name, taskType: m.taskType, category: tab } });
    dispatch({ type: 'RESET_PARAMS', payload: defaultParams(m.id) });
    setDetailModel(m);
    toast(`Selected: ${m.name}`, 'info');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: t.text, marginBottom: 6 }}>Select a Model</h2>
        <p style={{ color: t.muted, fontSize: 14 }}>Choose the algorithm that best fits your problem.</p>
      </div>

      {/* Recommendation banner */}
      {recModel && (
        <div style={{
          background: `${t.accent}15`, border: `1px solid ${t.accent}44`,
          borderRadius: 10, padding: '12px 16px',
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <span style={{ fontSize: 20 }}>✨</span>
          <div style={{ flex: 1 }}>
            <span style={{ color: t.accent, fontWeight: 700, fontSize: 14 }}>Recommended: </span>
            <span style={{ color: t.text, fontSize: 14 }}>{recModel.name}</span>
            <p style={{ color: t.muted, fontSize: 12, marginTop: 2 }}>Based on your data profile</p>
          </div>
          <Button dark={dark} size="sm" onClick={() => { setActiveTab(recommendedTab); selectModel(recModel, recommendedTab); }}>
            Use It
          </Button>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, borderBottom: `1px solid ${t.border}`, paddingBottom: 0 }}>
        {TABS.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={{
            padding: '8px 16px', background: 'none', border: 'none',
            borderBottom: activeTab === tab ? `2px solid ${t.accent}` : '2px solid transparent',
            color: activeTab === tab ? t.accent : t.muted,
            fontFamily: 'DM Sans, sans-serif', fontWeight: 600, fontSize: 13,
            cursor: 'pointer', transition: t.trans, marginBottom: -1,
          }}>{tab}</button>
        ))}
      </div>

      {/* Model grid + detail panel */}
      <div style={{ display: 'flex', gap: 20, alignItems: 'flex-start' }}>
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
          {(MODEL_CATALOG[activeTab] || []).map(m => {
            const selected = model.id === m.id;
            const isRec    = m.id === (recommendations[activeTab] ?? recommendation);
            return (
              <div key={m.id} onClick={() => selectModel(m, activeTab)} style={{
                background: t.card, border: `2px solid ${selected ? t.accent : t.border}`,
                borderRadius: 10, padding: 16, cursor: 'pointer',
                transition: t.trans, position: 'relative',
                boxShadow: selected ? `0 0 0 3px ${t.accent}33` : t.shadow,
              }}>
                {isRec && (
                  <div style={{ position: 'absolute', top: 10, right: 10 }}>
                    <Badge color={t.accent}>Recommended</Badge>
                  </div>
                )}
                <p style={{ fontWeight: 700, fontSize: 14, color: t.text, marginBottom: 6, paddingRight: isRec ? 90 : 0 }}>{m.name}</p>
                <p style={{ color: t.muted, fontSize: 12, lineHeight: 1.5, marginBottom: 10 }}>{m.desc}</p>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  <Badge color={COMPLEXITY_COLOR[m.complexity]}>{m.complexity} Complexity</Badge>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detail panel */}
        {detailModel && (
          <div style={{
            width: 260, flexShrink: 0,
            background: t.card, border: `1px solid ${t.border}`,
            borderRadius: 10, padding: 20, position: 'sticky', top: 20,
          }}>
            <p style={{ fontWeight: 700, fontSize: 16, color: t.text, marginBottom: 8 }}>{detailModel.name}</p>
            <Badge color={COMPLEXITY_COLOR[detailModel.complexity]} style={{ marginBottom: 10 }}>{detailModel.complexity} Complexity</Badge>
            <p style={{ color: t.muted, fontSize: 13, lineHeight: 1.6, marginTop: 10 }}>{detailModel.desc}</p>
            <div style={{ marginTop: 14, padding: '10px 12px', background: `${t.accent}0d`, borderRadius: 8 }}>
              <p style={{ color: t.accent, fontWeight: 600, fontSize: 12, marginBottom: 4 }}>Best Use</p>
              <p style={{ color: t.text, fontSize: 13, lineHeight: 1.5 }}>{detailModel.bestUse}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// STEP 3 — CONFIGURE FEATURES
// ─────────────────────────────────────────────
function StepFeatures({ state, dispatch }) {
  const { data, features, model, ui } = state;
  const dark = ui.darkMode;
  const t = tok(dark);
  const isTimeSeries = model.taskType === 'timeseries';

  const toggleInput = (col) => {
    const next = features.inputs.includes(col)
      ? features.inputs.filter(c => c !== col)
      : [...features.inputs, col];
    dispatch({ type: 'SET_FEATURES', payload: { inputs: next } });
  };

  const numericCols = data.columns.filter(c => data.types[c.name] === 'numeric').map(c => c.name);
  const correlations = useMemo(() => {
    if (!features.target || data.preview.length === 0) return {};
    const corrs = {};
    numericCols.forEach(col => {
      if (col === features.target) return;
      const xs = data.preview.map(r => parseFloat(r[col])).filter(v => !isNaN(v));
      const ys = data.preview.map(r => parseFloat(r[features.target])).filter(v => !isNaN(v));
      if (xs.length < 2) { corrs[col] = 0; return; }
      const n  = Math.min(xs.length, ys.length);
      const mx = xs.slice(0, n).reduce((a, b) => a + b, 0) / n;
      const my = ys.slice(0, n).reduce((a, b) => a + b, 0) / n;
      let num = 0, dx = 0, dy = 0;
      for (let i = 0; i < n; i++) {
        num += (xs[i] - mx) * (ys[i] - my);
        dx  += (xs[i] - mx) ** 2;
        dy  += (ys[i] - my) ** 2;
      }
      corrs[col] = dx && dy ? num / Math.sqrt(dx * dy) : 0;
    });
    return corrs;
  }, [features.target, data.preview, numericCols]);

  const topCorrelated = Object.entries(correlations)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 3)
    .filter(([, v]) => Math.abs(v) > 0.1);

  const corrColor = (v) => {
    const r = Math.round(255 * Math.max(0, v));
    const b = Math.round(255 * Math.max(0, -v));
    return `rgb(${r}, ${Math.round(255 * (1 - Math.abs(v)))}, ${b})`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: t.text, marginBottom: 6 }}>Configure Features</h2>
        <p style={{ color: t.muted, fontSize: 14 }}>Select input features and the target variable for your model.</p>
      </div>

      {/* Smart suggestion */}
      {topCorrelated.length > 0 && (
        <div style={{
          background: `${t.accent}0d`, border: `1px solid ${t.accent}33`,
          borderRadius: 8, padding: '10px 14px',
          display: 'flex', alignItems: 'flex-start', gap: 10,
        }}>
          <span style={{ fontSize: 16 }}>💡</span>
          <div>
            <p style={{ color: t.accent, fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
              Top correlated features with "{features.target}"
            </p>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {topCorrelated.map(([col, v]) => (
                <Badge key={col} color={t.accent}>{col} ({v.toFixed(2)})</Badge>
              ))}
            </div>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Left: feature checkboxes */}
        <div>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: t.text, marginBottom: 12 }}>
            Input Features ({features.inputs.length} selected)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 400, overflowY: 'auto', paddingRight: 4 }}>
            {data.columns.map(col => {
              const dtype = data.types[col.name] || 'text';
              const meta  = TYPE_META[dtype] || TYPE_META.text;
              const checked = features.inputs.includes(col.name);
              const isTarget = col.name === features.target;
              return (
                <label key={col.name} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '8px 12px', borderRadius: 8,
                  background: checked ? `${t.accent}0d` : t.card,
                  border: `1px solid ${checked ? t.accent + '44' : t.border}`,
                  cursor: isTarget ? 'not-allowed' : 'pointer',
                  opacity: isTarget ? 0.5 : 1,
                  transition: t.trans,
                }}>
                  <input type="checkbox" checked={checked} disabled={isTarget}
                    onChange={() => toggleInput(col.name)} />
                  <span style={{ flex: 1, fontSize: 13, color: t.text, fontWeight: checked ? 600 : 400 }}>{col.name}</span>
                  <Badge color={meta.color}>{meta.icon}</Badge>
                  {Object.hasOwn(correlations, col.name) && (
                    <span style={{
                      fontFamily: 'DM Mono, monospace', fontSize: 11,
                      color: corrColor(correlations[col.name]),
                      fontWeight: 600,
                    }}>{correlations[col.name].toFixed(2)}</span>
                  )}
                </label>
              );
            })}
          </div>
          <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
            <Button dark={dark} size="sm" variant="secondary"
              onClick={() => dispatch({ type: 'SET_FEATURES', payload: { inputs: data.columns.map(c => c.name).filter(n => n !== features.target) } })}>
              Select All
            </Button>
            <Button dark={dark} size="sm" variant="ghost"
              onClick={() => dispatch({ type: 'SET_FEATURES', payload: { inputs: [] } })}>
              Clear
            </Button>
          </div>
        </div>

        {/* Right: target + date dropdowns + correlation table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div>
            <label style={{ fontSize: 13, fontWeight: 600, color: t.text, display: 'block', marginBottom: 6 }}>
              Target Column
            </label>
            <select value={features.target}
              onChange={e => dispatch({ type: 'SET_FEATURES', payload: { target: e.target.value } })}
              style={{
                width: '100%', padding: '9px 12px', borderRadius: 8,
                border: `1px solid ${t.border}`, background: t.inputBg, color: t.text,
                fontSize: 14, transition: t.trans,
              }}>
              <option value="">— Select target —</option>
              {data.columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
            </select>
          </div>

          {isTimeSeries && (
            <div>
              <label style={{ fontSize: 13, fontWeight: 600, color: t.text, display: 'block', marginBottom: 6 }}>
                Date Column
              </label>
              <select value={features.dateColumn}
                onChange={e => dispatch({ type: 'SET_FEATURES', payload: { dateColumn: e.target.value } })}
                style={{
                  width: '100%', padding: '9px 12px', borderRadius: 8,
                  border: `1px solid ${t.border}`, background: t.inputBg, color: t.text,
                  fontSize: 14, transition: t.trans,
                }}>
                <option value="">— Select date column —</option>
                {data.columns.filter(c => data.types[c.name] === 'datetime').map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
              </select>
            </div>
          )}

          {/* Correlation table */}
          {features.target && numericCols.length > 1 && (
            <div>
              <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 8 }}>
                Correlation with "{features.target}"
              </h4>
              <div style={{ borderRadius: 8, border: `1px solid ${t.border}`, overflow: 'hidden' }}>
                {numericCols.filter(c => c !== features.target && Object.hasOwn(correlations, c)).slice(0, 8).map((col, i) => {
                  const v = correlations[col] || 0;
                  const pct = Math.abs(v) * 100;
                  return (
                    <div key={col} style={{
                      display: 'flex', alignItems: 'center', gap: 10,
                      padding: '7px 10px',
                      background: i % 2 === 0 ? t.card : (dark ? '#162032' : '#f8fafc'),
                      borderBottom: `1px solid ${t.border}33`,
                    }}>
                      <span style={{ width: 100, fontSize: 12, color: t.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{col}</span>
                      <div style={{ flex: 1, height: 8, background: t.border, borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: corrColor(v), borderRadius: 4 }} />
                      </div>
                      <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: t.muted, width: 40, textAlign: 'right' }}>
                        {v.toFixed(2)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// STEP 4 — SET PARAMETERS
// ─────────────────────────────────────────────
function ParamSlider({ label, pkey, min, max, step = 1, value, onChange, tooltip, dark }) {
  const t = tok(dark);
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        <label style={{ fontSize: 13, fontWeight: 600, color: t.text }}>{label}</label>
        {tooltip && <HelpTip text={tooltip} dark={dark} />}
        <span style={{ marginLeft: 'auto', fontFamily: 'DM Mono, monospace', fontSize: 13, color: t.accent, fontWeight: 600 }}>{value}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(pkey, step < 1 ? parseFloat(e.target.value) : parseInt(e.target.value))}
        style={{ width: '100%' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: t.muted, marginTop: 2 }}>
        <span>{min}</span><span>{max}</span>
      </div>
    </div>
  );
}

function ParamSelect({ label, pkey, options, value, onChange, tooltip, dark }) {
  const t = tok(dark);
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        <label style={{ fontSize: 13, fontWeight: 600, color: t.text }}>{label}</label>
        {tooltip && <HelpTip text={tooltip} dark={dark} />}
      </div>
      <select value={value} onChange={e => onChange(pkey, e.target.value)} style={{
        width: '100%', padding: '8px 10px', borderRadius: 8,
        border: `1px solid ${t.border}`, background: t.inputBg, color: t.text,
        fontSize: 13, fontFamily: 'DM Sans, sans-serif',
      }}>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function ParamToggle({ label, pkey, value, onChange, tooltip, dark }) {
  const t = tok(dark);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
      <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
        <div onClick={() => onChange(pkey, !value)} style={{
          width: 40, height: 22, borderRadius: 11,
          background: value ? t.accent : t.border,
          position: 'relative', transition: t.trans, cursor: 'pointer',
        }}>
          <div style={{
            position: 'absolute', top: 3, left: value ? 21 : 3,
            width: 16, height: 16, borderRadius: '50%',
            background: '#fff', transition: t.trans,
          }} />
        </div>
        <span style={{ fontSize: 13, fontWeight: 600, color: t.text }}>{label}</span>
      </label>
      {tooltip && <HelpTip text={tooltip} dark={dark} />}
    </div>
  );
}

function ModelParamForm({ modelId, params, setParam, dark }) {
  const t = tok(dark);
  const isDeep = ['mlp', 'lstm', 'cnn_1d', 'autoencoder'].includes(modelId);

  if (isDeep) return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 24px' }}>
      <div>
        <p style={{ fontSize: 12, fontWeight: 700, color: t.muted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Architecture</p>
        <ParamSlider label="Units per Layer" pkey="units" min={16} max={256} step={16} value={params.units ?? 64} onChange={setParam} tooltip="Number of neurons in each hidden layer." dark={dark} />
        <ParamSlider label="Number of Layers" pkey="layers" min={1} max={4} value={params.layers ?? 2} onChange={setParam} tooltip="Depth of the network. More layers = more capacity." dark={dark} />
        <ParamSlider label="Dropout Rate" pkey="dropout" min={0} max={0.5} step={0.05} value={params.dropout ?? 0.2} onChange={setParam} tooltip="Randomly drops neurons during training to prevent overfitting." dark={dark} />
        <ParamSelect label="Activation" pkey="activation" value={params.activation ?? 'relu'} options={['relu','tanh','sigmoid','elu','selu']} onChange={setParam} tooltip="Non-linear function applied after each layer." dark={dark} />
        <ParamSelect label="Weight Init" pkey="weight_init" value={params.weight_init ?? 'glorot_uniform'} options={['glorot_uniform','glorot_normal','he_normal','he_uniform','zeros']} onChange={setParam} tooltip="Strategy for initializing model weights." dark={dark} />
        {modelId === 'lstm' && <>
          <ParamToggle label="Bidirectional" pkey="bidirectional" value={params.bidirectional ?? false} onChange={setParam} tooltip="Process sequence in both directions for richer context." dark={dark} />
          <ParamToggle label="Return Sequences" pkey="return_sequences" value={params.return_sequences ?? false} onChange={setParam} tooltip="Return output at each timestep, not just the last." dark={dark} />
          <ParamToggle label="Stateful" pkey="stateful" value={params.stateful ?? false} onChange={setParam} tooltip="Carry hidden state across batches during training." dark={dark} />
        </>}
      </div>
      <div>
        <p style={{ fontSize: 12, fontWeight: 700, color: t.muted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Training</p>
        <ParamSelect label="Optimizer" pkey="optimizer" value={params.optimizer ?? 'adam'} options={['adam','sgd','rmsprop','adamw','adagrad']} onChange={setParam} tooltip="Algorithm used to update weights during training." dark={dark} />
        <ParamSlider label="Learning Rate" pkey="learning_rate" min={0.0001} max={0.1} step={0.0001} value={params.learning_rate ?? 0.001} onChange={setParam} tooltip="Step size for weight updates. Too high = instability; too low = slow." dark={dark} />
        <ParamSelect label="LR Scheduler" pkey="lr_scheduler" value={params.lr_scheduler ?? 'none'} options={['none','step','cosine','reduce_on_plateau']} onChange={setParam} tooltip="Automatically adjusts learning rate during training." dark={dark} />
        <ParamSelect label="Loss Function" pkey="loss" value={params.loss ?? 'mse'} options={['mse','mae','huber','binary_crossentropy','categorical_crossentropy']} onChange={setParam} tooltip="Objective the model minimizes during training." dark={dark} />
        <ParamSlider label="Epochs" pkey="epochs" min={10} max={200} step={10} value={params.epochs ?? 50} onChange={setParam} tooltip="Number of full passes over the training data." dark={dark} />
        <ParamSelect label="Batch Size" pkey="batch_size" value={String(params.batch_size ?? 32)} options={['16','32','64','128','256']} onChange={(k, v) => setParam(k, parseInt(v))} tooltip="Number of samples per gradient update." dark={dark} />
        <ParamSlider label="Validation Split" pkey="validation_split" min={0.05} max={0.2} step={0.05} value={params.validation_split ?? 0.1} onChange={setParam} tooltip="Fraction of training data held out to monitor validation loss." dark={dark} />
        <p style={{ fontSize: 12, fontWeight: 700, color: t.muted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12, marginTop: 8 }}>Regularization</p>
        <ParamSelect label="Type" pkey="reg_type" value={params.reg_type ?? 'none'} options={['none','l1','l2','elasticnet']} onChange={setParam} tooltip="Penalty applied to weights to prevent overfitting." dark={dark} />
        {params.reg_type && params.reg_type !== 'none' && (
          <ParamSlider label="Lambda" pkey="reg_lambda" min={0.0001} max={0.1} step={0.0001} value={params.reg_lambda ?? 0.001} onChange={setParam} tooltip="Strength of regularization penalty." dark={dark} />
        )}
        <ParamToggle label="Early Stopping" pkey="early_stopping" value={params.early_stopping ?? false} onChange={setParam} tooltip="Stop training when validation loss stops improving." dark={dark} />
        {params.early_stopping && (
          <ParamSlider label="Patience" pkey="patience" min={5} max={50} value={params.patience ?? 10} onChange={setParam} tooltip="Epochs to wait for improvement before stopping." dark={dark} />
        )}
      </div>
    </div>
  );

  // Classical models
  const rf = modelId.includes('random_forest');
  const xgb = modelId.includes('xgboost');
  const gb = modelId.includes('gradient_boosting');

  if (rf) return <>
    <ParamSlider label="Number of Trees" pkey="n_estimators" min={10} max={500} step={10} value={params.n_estimators ?? 100} onChange={setParam} tooltip="More trees = more stable predictions, but slower training." dark={dark} />
    <ParamSlider label="Max Depth" pkey="max_depth" min={1} max={30} value={params.max_depth ?? 10} onChange={setParam} tooltip="Maximum depth of each tree. Deeper = more complex, risk overfitting." dark={dark} />
    <ParamSlider label="Min Samples Split" pkey="min_samples_split" min={2} max={20} value={params.min_samples_split ?? 2} onChange={setParam} tooltip="Minimum samples required to split a node." dark={dark} />
  </>;

  if (xgb) return <>
    <ParamSlider label="Learning Rate" pkey="learning_rate" min={0.01} max={0.3} step={0.01} value={params.learning_rate ?? 0.1} onChange={setParam} tooltip="Shrinks contribution of each tree. Lower = more robust." dark={dark} />
    <ParamSlider label="Number of Trees" pkey="n_estimators" min={50} max={500} step={10} value={params.n_estimators ?? 100} onChange={setParam} tooltip="Number of boosting rounds." dark={dark} />
    <ParamSlider label="Max Depth" pkey="max_depth" min={1} max={15} value={params.max_depth ?? 5} onChange={setParam} tooltip="Maximum depth of each tree." dark={dark} />
    <ParamSlider label="Subsample" pkey="subsample" min={0.5} max={1.0} step={0.05} value={params.subsample ?? 0.8} onChange={setParam} tooltip="Fraction of samples used per tree. Lower = more regularization." dark={dark} />
    <ParamSlider label="Col Sample per Tree" pkey="colsample_bytree" min={0.5} max={1.0} step={0.05} value={params.colsample_bytree ?? 0.8} onChange={setParam} tooltip="Fraction of features used per tree." dark={dark} />
  </>;

  if (gb) return <>
    <ParamSlider label="Learning Rate" pkey="learning_rate" min={0.01} max={0.3} step={0.01} value={params.learning_rate ?? 0.1} onChange={setParam} tooltip="Step size shrinkage used in each iteration." dark={dark} />
    <ParamSlider label="Number of Estimators" pkey="n_estimators" min={50} max={500} step={10} value={params.n_estimators ?? 100} onChange={setParam} tooltip="Number of boosting stages to perform." dark={dark} />
    <ParamSlider label="Max Depth" pkey="max_depth" min={1} max={10} value={params.max_depth ?? 3} onChange={setParam} tooltip="Maximum depth of individual trees." dark={dark} />
  </>;

  if (modelId === 'logistic_regression') return <>
    <ParamSlider label="Regularization C" pkey="C" min={0.01} max={10} step={0.01} value={params.C ?? 1.0} onChange={setParam} tooltip="Inverse of regularization strength. Smaller = more regularization." dark={dark} />
    <ParamSlider label="Max Iterations" pkey="max_iter" min={100} max={1000} step={50} value={params.max_iter ?? 200} onChange={setParam} tooltip="Maximum iterations for solver convergence." dark={dark} />
    <ParamSelect label="Solver" pkey="solver" value={params.solver ?? 'lbfgs'} options={['lbfgs','liblinear','saga','newton-cg']} onChange={setParam} tooltip="Algorithm used to optimize the loss function." dark={dark} />
  </>;

  if (modelId === 'arima') return <>
    <ParamSlider label="p (AR order)" pkey="p" min={0} max={5} value={params.p ?? 1} onChange={setParam} tooltip="Number of autoregressive terms (lag observations)." dark={dark} />
    <ParamSlider label="d (Differencing)" pkey="d" min={0} max={2} value={params.d ?? 1} onChange={setParam} tooltip="Degree of differencing to make series stationary." dark={dark} />
    <ParamSlider label="q (MA order)" pkey="q" min={0} max={5} value={params.q ?? 1} onChange={setParam} tooltip="Number of moving average terms." dark={dark} />
  </>;

  if (modelId === 'sarima') return <>
    <ParamSlider label="p" pkey="p" min={0} max={5} value={params.p ?? 1} onChange={setParam} tooltip="Non-seasonal AR order." dark={dark} />
    <ParamSlider label="d" pkey="d" min={0} max={2} value={params.d ?? 1} onChange={setParam} tooltip="Non-seasonal differencing." dark={dark} />
    <ParamSlider label="q" pkey="q" min={0} max={5} value={params.q ?? 1} onChange={setParam} tooltip="Non-seasonal MA order." dark={dark} />
    <ParamSlider label="P (Seasonal AR)" pkey="P" min={0} max={3} value={params.P ?? 1} onChange={setParam} tooltip="Seasonal autoregressive order." dark={dark} />
    <ParamSlider label="D (Seasonal diff)" pkey="D" min={0} max={2} value={params.D ?? 1} onChange={setParam} tooltip="Seasonal differencing order." dark={dark} />
    <ParamSlider label="Q (Seasonal MA)" pkey="Q" min={0} max={3} value={params.Q ?? 1} onChange={setParam} tooltip="Seasonal moving average order." dark={dark} />
    <ParamSlider label="m (Seasonal Period)" pkey="m" min={2} max={52} value={params.m ?? 12} onChange={setParam} tooltip="Number of periods in a season (e.g., 12 for monthly data)." dark={dark} />
  </>;

  if (modelId === 'kmeans') return <>
    <ParamSlider label="Number of Clusters" pkey="n_clusters" min={2} max={15} value={params.n_clusters ?? 4} onChange={setParam} tooltip="Number of groups to partition data into." dark={dark} />
    <ParamSelect label="Initialization" pkey="init" value={params.init ?? 'k-means++'} options={['k-means++','random']} onChange={setParam} tooltip="Method for choosing initial cluster centroids." dark={dark} />
    <ParamSlider label="Max Iterations" pkey="max_iter" min={100} max={500} step={50} value={params.max_iter ?? 300} onChange={setParam} tooltip="Maximum iterations for centroid convergence." dark={dark} />
  </>;

  if (modelId === 'svm_classifier' || modelId === 'svr') return <>
    <ParamSlider label="C (Regularization)" pkey="C" min={0.01} max={10} step={0.01} value={params.C ?? 1.0} onChange={setParam} tooltip="Penalty for misclassification. Higher = less margin allowed." dark={dark} />
    <ParamSelect label="Kernel" pkey="kernel" value={params.kernel ?? 'rbf'} options={['linear','rbf','poly','sigmoid']} onChange={setParam} tooltip="Type of decision boundary to learn." dark={dark} />
    <ParamSelect label="Gamma" pkey="gamma" value={params.gamma ?? 'scale'} options={['scale','auto']} onChange={setParam} tooltip="Kernel coefficient — how far the influence of each sample reaches." dark={dark} />
  </>;

  if (modelId === 'knn') return <>
    <ParamSlider label="K Neighbors" pkey="n_neighbors" min={1} max={20} value={params.n_neighbors ?? 5} onChange={setParam} tooltip="Number of nearest neighbors to consider for classification." dark={dark} />
  </>;

  if (modelId === 'ridge' || modelId === 'lasso') return <>
    <ParamSlider label="Alpha (Regularization)" pkey="alpha" min={0.01} max={10} step={0.01} value={params.alpha ?? 1.0} onChange={setParam} tooltip="Strength of regularization. Higher = more penalty on large weights." dark={dark} />
  </>;

  if (modelId === 'dbscan') return <>
    <ParamSlider label="Epsilon (eps)" pkey="eps" min={0.1} max={2.0} step={0.1} value={params.eps ?? 0.5} onChange={setParam} tooltip="Maximum distance between two samples to be considered neighbors." dark={dark} />
    <ParamSlider label="Min Samples" pkey="min_samples" min={2} max={10} value={params.min_samples ?? 5} onChange={setParam} tooltip="Minimum points to form a dense region (core point)." dark={dark} />
  </>;

  if (modelId === 'hierarchical') return <>
    <ParamSlider label="Number of Clusters" pkey="n_clusters" min={2} max={15} value={params.n_clusters ?? 4} onChange={setParam} tooltip="Number of clusters to find in the hierarchy." dark={dark} />
    <ParamSelect label="Linkage" pkey="linkage" value={params.linkage ?? 'ward'} options={['ward','complete','average','single']} onChange={setParam} tooltip="Criterion for merging clusters. Ward minimizes variance." dark={dark} />
  </>;

  if (modelId === 'exponential_smoothing') return <>
    <ParamSelect label="Trend" pkey="trend" value={params.trend ?? 'add'} options={['add','mul','none']} onChange={setParam} tooltip="Type of trend component: additive, multiplicative, or none." dark={dark} />
    <ParamSelect label="Seasonal" pkey="seasonal" value={params.seasonal ?? 'add'} options={['add','mul','none']} onChange={setParam} tooltip="Type of seasonal component." dark={dark} />
    <ParamSlider label="Seasonal Periods" pkey="seasonal_periods" min={4} max={52} value={params.seasonal_periods ?? 12} onChange={setParam} tooltip="Number of periods in one seasonal cycle." dark={dark} />
  </>;

  return (
    <div style={{ padding: 20, textAlign: 'center', color: t.muted, fontSize: 14 }}>
      No parameters to configure for this model.
    </div>
  );
}

function StepParams({ state, dispatch }) {
  const { model, params, split, data, ui, features } = state;
  const dark = ui.darkMode;
  const t = tok(dark);
  const toast = useToast();
  const [training, setTraining] = useState(false);
  const isDeep = ['mlp','lstm','cnn_1d','autoencoder'].includes(model.id);

  const setParam = useCallback((key, value) => {
    dispatch({ type: 'SET_PARAMS', payload: { [key]: value } });
  }, [dispatch]);

  const trainRows = Math.round((data.shape.rows || 1000) * (1 - split.testSize));
  const testRows  = (data.shape.rows || 1000) - trainRows;

  const handleTrain = async () => {
    setTraining(true);
    dispatch({ type: 'SET_UI', payload: { loading: true, error: null } });
    toast('Training started...', 'info');
    try {
      const body = {
        file_id:         data.fileId,
        model_type:      model.id,
        feature_columns: features.inputs,
        target_column:   features.target,
        params,
        test_size:   split.testSize,
        cv_folds:    split.useCv ? split.cvFolds : null,
        date_column: features.dateColumn || null,
      };
      const res = await fetch('http://localhost:8000/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Training failed'); }
      const json = await res.json();
      dispatch({ type: 'SET_RESULTS', payload: { current: { ...json, modelName: model.name, modelId: model.id, params: { ...params }, timestamp: new Date().toISOString() } } });
      dispatch({ type: 'SET_UI', payload: { step: 5 } });
      toast('Training complete!', 'success');
    } catch (err) {
      dispatch({ type: 'SET_UI', payload: { error: err.message } });
      toast(err.message, 'error');
    } finally {
      setTraining(false);
      dispatch({ type: 'SET_UI', payload: { loading: false } });
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: t.text, marginBottom: 6 }}>Set Parameters</h2>
        <p style={{ color: t.muted, fontSize: 14 }}>Tune hyperparameters for <strong>{model.name}</strong>.</p>
      </div>

      {/* Presets */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: t.muted }}>Quick Presets:</span>
        {['conservative','balanced','aggressive'].map(p => (
          <Button key={p} dark={dark} size="sm" variant="secondary"
            onClick={() => { dispatch({ type: 'RESET_PARAMS', payload: PRESETS[p](model.id) }); toast(`Applied ${p} preset`, 'info'); }}>
            {p.charAt(0).toUpperCase() + p.slice(1)}
          </Button>
        ))}
      </div>

      {/* Params */}
      <Card dark={dark}>
        <ModelParamForm modelId={model.id} params={params} setParam={setParam} dark={dark} />
      </Card>

      {/* Train/Test Split */}
      <Card dark={dark}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 14 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: t.text }}>Train / Test Split</h3>
          <HelpTip text="Fraction of data reserved for testing model performance." dark={dark} />
        </div>
        <ParamSlider
          label={`Test Size: ${Math.round(split.testSize * 100)}%`}
          pkey="testSize" min={0.1} max={0.4} step={0.05}
          value={split.testSize}
          onChange={(_, v) => dispatch({ type: 'SET_SPLIT', payload: { testSize: v } })}
          dark={dark}
        />
        <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
          <div style={{ flex: 1 - split.testSize, background: `${t.accent}22`, border: `1px solid ${t.accent}44`, borderRadius: 6, padding: '8px 12px', textAlign: 'center' }}>
            <p style={{ fontFamily: 'DM Mono, monospace', fontSize: 18, fontWeight: 700, color: t.accent }}>{trainRows.toLocaleString()}</p>
            <p style={{ fontSize: 12, color: t.muted }}>Training rows ({Math.round((1 - split.testSize) * 100)}%)</p>
          </div>
          <div style={{ flex: split.testSize, background: `#f59e0b22`, border: `1px solid #f59e0b44`, borderRadius: 6, padding: '8px 12px', textAlign: 'center' }}>
            <p style={{ fontFamily: 'DM Mono, monospace', fontSize: 18, fontWeight: 700, color: '#f59e0b' }}>{testRows.toLocaleString()}</p>
            <p style={{ fontSize: 12, color: t.muted }}>Testing rows ({Math.round(split.testSize * 100)}%)</p>
          </div>
        </div>

        {!isDeep && (
          <div style={{ marginTop: 16, paddingTop: 16, borderTop: `1px solid ${t.border}` }}>
            <ParamToggle label="Cross-Validation" pkey="useCv" value={split.useCv}
              onChange={(_, v) => dispatch({ type: 'SET_SPLIT', payload: { useCv: v } })}
              tooltip="Evaluate model stability across multiple data splits." dark={dark} />
            {split.useCv && (
              <ParamSlider label="K Folds" pkey="cvFolds" min={3} max={10} value={split.cvFolds}
                onChange={(_, v) => dispatch({ type: 'SET_SPLIT', payload: { cvFolds: v } })}
                tooltip="Number of cross-validation folds." dark={dark} />
            )}
          </div>
        )}
      </Card>

      {/* Train button */}
      <Button dark={dark} size="lg" onClick={handleTrain} disabled={training}
        style={{ width: '100%', padding: '16px', fontSize: 16, letterSpacing: 0.5 }}>
        {training ? <><Spinner color="#fff" /> Training Model...</> : 'Train Model'}
      </Button>
    </div>
  );
}

// ─────────────────────────────────────────────
// STEP 5 — RESULTS
// ─────────────────────────────────────────────
const METRIC_INFO = {
  mae:       { label: 'MAE',        good: [0, 0.1],  ok: [0.1, 0.3],  unit: '',    desc: 'Mean Absolute Error — average magnitude of errors.', higher_better: false },
  mse:       { label: 'MSE',        good: [0, 0.05], ok: [0.05, 0.2], unit: '',    desc: 'Mean Squared Error — penalizes large errors more.', higher_better: false },
  rmse:      { label: 'RMSE',       good: [0, 0.1],  ok: [0.1, 0.3],  unit: '',    desc: 'Root Mean Squared Error — same unit as target.', higher_better: false },
  mape:      { label: 'MAPE',       good: [0, 5],    ok: [5, 15],     unit: '%',   desc: 'Mean Absolute Percentage Error — relative accuracy.', higher_better: false },
  r2:        { label: 'R²',         good: [0.9, 1],  ok: [0.7, 0.9],  unit: '',    desc: 'R-squared — proportion of variance explained. 1.0 is perfect.', higher_better: true },
  accuracy:  { label: 'Accuracy',   good: [0.9, 1],  ok: [0.7, 0.9],  unit: '',    desc: 'Fraction of correctly classified samples.', higher_better: true },
  precision: { label: 'Precision',  good: [0.9, 1],  ok: [0.7, 0.9],  unit: '',    desc: 'Of all positive predictions, how many were correct?', higher_better: true },
  recall:    { label: 'Recall',     good: [0.9, 1],  ok: [0.7, 0.9],  unit: '',    desc: 'Of all actual positives, how many were found?', higher_better: true },
  f1:        { label: 'F1 Score',   good: [0.9, 1],  ok: [0.7, 0.9],  unit: '',    desc: 'Harmonic mean of precision and recall.', higher_better: true },
  roc_auc:   { label: 'ROC-AUC',    good: [0.9, 1],  ok: [0.7, 0.9],  unit: '',    desc: 'Area under the ROC curve. 1.0 = perfect, 0.5 = random.', higher_better: true },
  silhouette:{ label: 'Silhouette', good: [0.6, 1],  ok: [0.3, 0.6],  unit: '',    desc: 'Measures how similar a point is to its own cluster vs others.', higher_better: true },
  inertia:   { label: 'Inertia',    good: [0, 100],  ok: [100, 500],  unit: '',    desc: 'Sum of squared distances to cluster centroids. Lower is better.', higher_better: false },
};

function metricColor(key, value) {
  const info = METRIC_INFO[key];
  if (!info) return '#5565a0';
  const v = parseFloat(value);
  const [g0, g1] = info.good;
  const [o0, o1] = info.ok;
  if (info.higher_better) {
    if (v >= g0) return '#39ff14';
    if (v >= o0) return '#ffbe0b';
    return '#ff006e';
  } else {
    if (v <= g1) return '#39ff14';
    if (v <= o1) return '#ffbe0b';
    return '#ff006e';
  }
}

function MetricCard({ mkey, value, dark }) {
  const t = tok(dark ?? true);
  const info = METRIC_INFO[mkey] || { label: mkey, desc: '', unit: '' };
  const color = metricColor(mkey, value);
  const display = typeof value === 'number' ? value.toFixed(4) : String(value ?? '—');
  return (
    <div style={{
      background: t.card, border: `1px solid ${color}33`,
      borderRadius: t.radius, padding: '16px 14px',
      borderTop: `2px solid ${color}`,
      boxShadow: `${t.shadow}, 0 0 16px ${color}18`,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
        <p style={{ fontSize: 10, fontWeight: 600, color: t.muted, textTransform: 'uppercase', letterSpacing: 1, fontFamily: 'Share Tech Mono, monospace' }}>{info.label}</p>
        <HelpTip text={info.desc} dark={dark} />
      </div>
      <p style={{ fontFamily: 'Share Tech Mono, DM Mono, monospace', fontSize: 26, fontWeight: 700, color, textShadow: `0 0 10px ${color}` }}>{display}{info.unit}</p>
    </div>
  );
}

function ConfusionMatrix({ matrix, dark }) {
  const t = tok(dark);
  if (!matrix || !Array.isArray(matrix)) return null;
  const maxVal = Math.max(...matrix.flat());
  return (
    <div>
      <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 10 }}>Confusion Matrix</h4>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${matrix[0].length}, 1fr)`, gap: 2 }}>
        {matrix.map((row, i) => row.map((val, j) => {
          const intensity = maxVal > 0 ? val / maxVal : 0;
          const bg = i === j
            ? `rgba(0, 255, 213, ${0.15 + intensity * 0.6})`
            : `rgba(255, 0, 110, ${intensity * 0.45})`;
          return (
            <div key={`${i}-${j}`} style={{
              background: bg, borderRadius: 4, padding: '12px 8px',
              textAlign: 'center', fontFamily: 'DM Mono, monospace',
              fontSize: 16, fontWeight: 700, color: t.text,
            }}>{val}</div>
          );
        }))}
      </div>
    </div>
  );
}

function StepResults({ state, dispatch }) {
  const { results, model, ui, data, features } = state;
  const dark = ui.darkMode;
  const t = tok(dark);
  const toast = useToast();
  const current = results.current;

  if (!current) {
    return (
      <div style={{ textAlign: 'center', padding: 60, color: t.muted }}>
        <div style={{ marginBottom: 16, color: '#5565a0' }}><CyberIcon name="chart" size={48} color="#5565a0" /></div>
        <p style={{ fontSize: 16 }}>No results yet. Complete training to see results.</p>
      </div>
    );
  }

  const metrics  = current.metrics || {};
  const taskType = current.task_type || model.taskType;

  const regressionMetrics    = ['mae','mse','rmse','mape','r2'].filter(k => k in metrics);
  const classificationMetrics= ['accuracy','precision','recall','f1','roc_auc'].filter(k => k in metrics);
  const clusteringMetrics    = ['silhouette','inertia'].filter(k => k in metrics);

  const displayMetrics = taskType === 'regression' ? regressionMetrics
    : taskType === 'classification' ? classificationMetrics
    : clusteringMetrics;

  const addToComparison = () => {
    const comp = results.comparison || [];
    if (comp.length >= 3) { toast('Max 3 models for comparison', 'error'); return; }
    if (comp.find(x => x.modelId === current.modelId && JSON.stringify(x.params) === JSON.stringify(current.params))) {
      toast('Already in comparison', 'error'); return;
    }
    dispatch({ type: 'SET_RESULTS', payload: { comparison: [...comp, current] } });
    toast('Added to comparison!', 'success');
  };

  const saveResults = () => {
    const blob = new Blob([JSON.stringify(current, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `${current.modelId}_results_${Date.now()}.json`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast('Results saved!', 'success');
  };

  const exportReport = () => { try {
    const m   = current.metrics || {};
    // Normalize — backend may return dicts instead of arrays
    const fiRaw = current.feature_importances;
    const fi  = Array.isArray(fiRaw) ? fiRaw
              : (fiRaw && typeof fiRaw === 'object')
                ? Object.entries(fiRaw).map(([feature, importance]) => ({ feature, importance }))
                : [];
    const avpRaw = current.actual_vs_predicted;
    const avp = Array.isArray(avpRaw) ? avpRaw : [];
    const res = Array.isArray(current.residuals) ? current.residuals : [];
    const cm  = current.confusion_matrix || null;
    const rocRaw = current.roc_curve;
    const roc = Array.isArray(rocRaw) ? rocRaw : [];
    const pcaRaw = current.pca_2d;
    const pca = Array.isArray(pcaRaw) ? pcaRaw : [];

    const fiShown  = Math.min(20, fi.length);
    const avpShown = Math.min(50, avp.length);
    const resShown = Math.min(50, res.length);
    const rocShown = Math.min(20, roc.length);
    const pcaShown = Math.min(50, pca.length);

    const fiRows = fi.slice(0, fiShown).map(({feature, importance}) =>
      `<tr><td>${feature}</td><td>${typeof importance === 'number' ? importance.toFixed(6) : importance}</td></tr>`).join('');

    const avpRows = avp.slice(0, avpShown).map(({actual, predicted}) =>
      `<tr><td>${typeof actual==='number'?actual.toFixed(4):actual}</td><td>${typeof predicted==='number'?predicted.toFixed(4):predicted}</td></tr>`).join('');

    const resRows = res.slice(0, resShown).map((v, i) =>
      `<tr><td>${i+1}</td><td>${typeof v==='number'?v.toFixed(6):v}</td></tr>`).join('');

    const rocRows = roc.slice(0, rocShown).map(({fpr, tpr}) =>
      `<tr><td>${typeof fpr==='number'?fpr.toFixed(4):fpr}</td><td>${typeof tpr==='number'?tpr.toFixed(4):tpr}</td></tr>`).join('');

    const cmHtml = cm ? `
      <div class="card" id="confmat">
        <h3>Confusion Matrix</h3>
        <table style="width:auto">
          ${cm.map(row=>`<tr>${row.map(v=>`<td style="text-align:center;min-width:48px;font-weight:700">${v}</td>`).join('')}</tr>`).join('')}
        </table>
      </div>` : '';

    const pcaRows = pca.slice(0, pcaShown).map(({x, y, cluster}) =>
      `<tr><td>${typeof x==='number'?x.toFixed(4):x}</td><td>${typeof y==='number'?y.toFixed(4):y}</td><td>${cluster ?? '—'}</td></tr>`).join('');

    const fiHeading  = fiShown  < fi.length  ? `A1 · Feature Importances (top ${fiShown})`            : 'A1 · Feature Importances';
    const fiNote     = fiShown  < fi.length  ? `Showing top ${fiShown} of ${fi.length} features.`     : `Showing all ${fi.length} features.`;
    const avpHeading = avpShown < avp.length ? `A2 · Actual vs Predicted (first ${avpShown} rows)`    : 'A2 · Actual vs Predicted';
    const avpNote    = avpShown < avp.length ? `Showing first ${avpShown} of ${avp.length} test samples.` : `Showing all ${avp.length} test samples.`;
    const resHeading = resShown < res.length ? `A3 · Residuals (first ${resShown} rows)`              : 'A3 · Residuals';
    const resNote    = resShown < res.length ? `Showing first ${resShown} of ${res.length} residuals.` : `Showing all ${res.length} residuals.`;
    const rocHeading = rocShown < roc.length ? 'A5 · ROC Curve Data (sample)'                         : 'A5 · ROC Curve Data';
    const rocNote    = rocShown < roc.length ? `Showing ${rocShown} evenly-spaced points of ${roc.length} total.` : `Showing all ${roc.length} ROC points.`;
    const pcaHeading = pcaShown < pca.length ? `A6 · PCA 2D Cluster Data (first ${pcaShown} points)`  : 'A6 · PCA 2D Cluster Data';
    const pcaNote    = pcaShown < pca.length ? `Showing first ${pcaShown} of ${pca.length} cluster points.` : `Showing all ${pca.length} cluster points.`;

    const html = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>HappyModel Report – ${current.modelName}</title>
<style>
  body{font-family:system-ui,sans-serif;background:#f8fafc;color:#0f172a;padding:40px;max-width:960px;margin:auto;line-height:1.6}
  h1{color:#00a896;border-bottom:2px solid #00a896;padding-bottom:12px;font-size:28px;margin-bottom:4px}
  h2{color:#0f172a;font-size:20px;margin:0 0 12px}
  h3{color:#334155;font-size:16px;margin:0 0 10px}
  .subtitle{color:#64748b;font-size:13px;margin-bottom:32px}
  .card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:24px;margin:20px 0;box-shadow:0 1px 3px rgba(0,0,0,.08)}
  .meta-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 24px;font-size:13px}
  .meta-grid span{color:#64748b}
  .metric{display:inline-block;margin:6px;padding:14px 20px;border-radius:8px;background:#f1f5f9;text-align:center;min-width:130px;border-top:3px solid #00a896}
  .metric small{display:block;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
  .metric b{display:block;font-size:22px;color:#00a896;font-family:monospace}
  table{width:100%;border-collapse:collapse;font-size:13px}
  td,th{padding:8px 12px;text-align:left;border-bottom:1px solid #e2e8f0}
  th{font-weight:600;background:#f8fafc;color:#475569}
  .appendix-label{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
  .note{font-size:12px;color:#94a3b8;margin-top:6px}
  @media print{.card{break-inside:avoid}}
</style></head><body>
<h1>HappyModel Report</h1>
<p class="subtitle">Generated by HappyModel · ${new Date(current.timestamp).toLocaleString()}</p>

<div class="card">
  <h2>Overview</h2>
  <div class="meta-grid">
    <div><span>Dataset</span><br/><strong>${data.fileName || '—'}</strong></div>
    <div><span>Model</span><br/><strong>${current.modelName}</strong></div>
    <div><span>Task Type</span><br/><strong>${(current.task_type||'').replace('_',' ')}</strong></div>
    <div><span>Training Time</span><br/><strong>${current.training_time != null ? Number(current.training_time).toFixed(2)+'s' : '—'}</strong></div>
    <div><span>Dataset Shape</span><br/><strong>${data.shape?.rows?.toLocaleString() || '—'} rows × ${data.shape?.cols || '—'} cols</strong></div>
    <div><span>Features Used</span><br/><strong>${features.inputs.length} columns</strong></div>
  </div>
</div>

<div class="card">
  <h2>Performance Metrics</h2>
  ${Object.entries(m).map(([k,v])=>`<div class="metric"><small>${k.toUpperCase()}</small><b>${typeof v==='number'?v.toFixed(4):v}</b></div>`).join('')}
</div>

<div class="card">
  <h2>Hyperparameters</h2>
  <table><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>
  ${Object.entries(current.params||{}).map(([k,v])=>`<tr><td>${k}</td><td><b>${v}</b></td></tr>`).join('')}
  </tbody></table>
</div>

<div class="card">
  <h2>Feature Configuration</h2>
  <p><strong>Target column:</strong> ${features.target || '—'}</p>
  <p style="margin-top:8px"><strong>Input features (${features.inputs.length}):</strong></p>
  <p style="color:#475569;font-size:13px;margin-top:4px">${features.inputs.join(', ') || '—'}</p>
</div>

<h2 style="margin-top:40px;padding-top:16px;border-top:2px solid #e2e8f0">Appendix — Full Data</h2>

${fi.length > 0 ? `<div class="card">
  <h3>${fiHeading}</h3>
  <table><thead><tr><th>Feature</th><th>Importance</th></tr></thead><tbody>${fiRows}</tbody></table>
  <p class="note">${fiNote}</p>
</div>` : ''}

${avp.length > 0 ? `<div class="card">
  <h3>${avpHeading}</h3>
  <table><thead><tr><th>Actual</th><th>Predicted</th></tr></thead><tbody>${avpRows}</tbody></table>
  <p class="note">${avpNote}</p>
</div>` : ''}

${res.length > 0 ? `<div class="card">
  <h3>${resHeading}</h3>
  <table><thead><tr><th>#</th><th>Residual (Actual − Predicted)</th></tr></thead><tbody>${resRows}</tbody></table>
  <p class="note">${resNote}</p>
</div>` : ''}

${cmHtml}

${roc.length > 0 ? `<div class="card">
  <h3>${rocHeading}</h3>
  <table><thead><tr><th>FPR</th><th>TPR</th></tr></thead><tbody>${rocRows}</tbody></table>
  <p class="note">${rocNote}</p>
</div>` : ''}

${pca.length > 0 ? `<div class="card">
  <h3>${pcaHeading}</h3>
  <table><thead><tr><th>PC1</th><th>PC2</th><th>Cluster</th></tr></thead><tbody>${pcaRows}</tbody></table>
  <p class="note">${pcaNote}</p>
</div>` : ''}

</body></html>`;

    // Use octet-stream so browser always downloads rather than rendering the HTML
    const blob = new Blob([html], { type: 'application/octet-stream' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `happymodel_report_${current.modelId}_${Date.now()}.html`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    toast('Report exported!', 'success');
  } catch(err) { toast('Export failed: ' + err.message, 'error'); } };

  const exportComparison = () => { try {
    if (comp.length < 2) { toast('Add at least 2 models to compare first', 'error'); return; }

    // Helper — normalize feature_importances whether it's an array or a dict
    const normFI = (v) => Array.isArray(v) ? v
      : (v && typeof v === 'object')
        ? Object.entries(v).map(([feature, importance]) => ({ feature, importance }))
        : [];

    // All metric keys across every compared model
    const allMetricKeys = [...new Set(comp.flatMap(c => Object.keys(c.metrics || {})))];

    // Side-by-side metrics table rows
    const metricRows = allMetricKeys.map(k => {
      const vals    = comp.map(c => c.metrics?.[k] ?? null);
      const numVals = vals.filter(v => v != null && !isNaN(v));
      const hiB     = METRIC_INFO[k]?.higher_better ?? true;
      const best    = numVals.length ? (hiB ? Math.max(...numVals) : Math.min(...numVals)) : null;
      const cells   = vals.map(v => {
        const isBest = v != null && v === best;
        const fmt    = v != null ? (typeof v === 'number' ? v.toFixed(4) : v) : '—';
        return `<td style="text-align:center;${isBest ? 'color:#00ffd5;font-weight:700;background:#00ffd510' : ''}">${fmt}</td>`;
      }).join('');
      return `<tr><td style="font-weight:600">${METRIC_INFO[k]?.label || k.toUpperCase()}</td>${cells}</tr>`;
    }).join('');

    // Per-model appendix sections
    const modelCards = comp.map((c, idx) => {
      const fi  = normFI(c.feature_importances);
      const avp = Array.isArray(c.actual_vs_predicted) ? c.actual_vs_predicted : [];
      const res = Array.isArray(c.residuals) ? c.residuals : [];
      const cm  = c.confusion_matrix || null;

      const fiShown  = Math.min(20, fi.length);
      const avpShown = Math.min(30, avp.length);
      const resShown = Math.min(30, res.length);
      const fiHead     = fiShown  < fi.length  ? `Feature Importances (top ${fiShown})`   : 'Feature Importances';
      const avpHead    = avpShown < avp.length ? `Actual vs Predicted (first ${avpShown})` : 'Actual vs Predicted';
      const resHead    = resShown < res.length ? `Residuals (first ${resShown})`           : 'Residuals';
      const fiCaption  = fiShown  === fi.length  ? `Showing all ${fi.length} features.`      : `Showing top ${fiShown} of ${fi.length} features.`;
      const avpCaption = avpShown === avp.length ? `Showing all ${avp.length} test samples.` : `Showing first ${avpShown} of ${avp.length} test samples.`;
      const resCaption = resShown === res.length ? `Showing all ${res.length} residuals.`    : `Showing first ${resShown} of ${res.length} residuals.`;
      const fiRows  = fi.slice(0, fiShown).map(({feature,importance}) =>
        `<tr><td>${feature}</td><td>${typeof importance==='number'?importance.toFixed(6):importance}</td></tr>`).join('');
      const avpRows = avp.slice(0, avpShown).map(({actual,predicted}) =>
        `<tr><td>${typeof actual==='number'?actual.toFixed(4):actual}</td><td>${typeof predicted==='number'?predicted.toFixed(4):predicted}</td></tr>`).join('');
      const resRows = res.slice(0, resShown).map((v,i) =>
        `<tr><td>${i+1}</td><td>${typeof v==='number'?v.toFixed(6):v}</td></tr>`).join('');
      const cmHtml  = cm ? `<h4 style="margin:16px 0 8px">Confusion Matrix</h4>
        <table style="width:auto">${cm.map(row=>`<tr>${row.map(v=>`<td style="text-align:center;min-width:40px;font-weight:700;padding:6px">${v}</td>`).join('')}</tr>`).join('')}</table>` : '';

      return `<div class="card">
  <h3 style="color:#00ffd5;margin-bottom:4px">Model ${idx+1}: ${c.modelName}</h3>
  <p style="color:#888;font-size:12px;margin-bottom:16px">
    Trained ${new Date(c.timestamp).toLocaleString()}
    ${c.training_time != null ? ' · ' + Number(c.training_time).toFixed(2) + 's' : ''}
  </p>
  <h4 style="margin-bottom:8px">Parameters</h4>
  <table style="width:auto;margin-bottom:16px">
    <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
    <tbody>${Object.entries(c.params||{}).map(([k,v])=>`<tr><td>${k}</td><td><b>${v}</b></td></tr>`).join('')}</tbody>
  </table>
  ${fi.length>0 ? `<h4 style="margin-bottom:8px">${fiHead}</h4>
  <table><thead><tr><th>Feature</th><th>Importance</th></tr></thead><tbody>${fiRows}</tbody></table>
  <p style="font-size:11px;color:#5565a0;margin-top:6px">${fiCaption}</p>` : ''}
  ${avp.length>0 ? `<h4 style="margin:16px 0 8px">${avpHead}</h4>
  <table><thead><tr><th>Actual</th><th>Predicted</th></tr></thead><tbody>${avpRows}</tbody></table>
  <p style="font-size:11px;color:#5565a0;margin-top:6px">${avpCaption}</p>` : ''}
  ${res.length>0 ? `<h4 style="margin:16px 0 8px">${resHead}</h4>
  <table><thead><tr><th>#</th><th>Residual</th></tr></thead><tbody>${resRows}</tbody></table>
  <p style="font-size:11px;color:#5565a0;margin-top:6px">${resCaption}</p>` : ''}
  ${cmHtml}
</div>`;
    }).join('');

    const modelHeaders = comp.map((c,i) => `<th style="text-align:center;color:#00ffd5;padding:10px 14px">${c.modelName}</th>`).join('');

    const html = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<title>HappyModel — Comparison Report</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,sans-serif;background:#0a0a14;color:#c0c8ff;padding:32px;line-height:1.6}
  h1{font-size:26px;color:#00ffd5;margin-bottom:4px;letter-spacing:1px}
  h2{font-size:18px;color:#c0c8ff;margin:28px 0 12px}
  h3{font-size:15px;color:#a0aec0;margin:20px 0 8px}
  h4{font-size:13px;color:#a0aec0}
  .subtitle{color:#5565a0;font-size:13px;margin-bottom:28px}
  .card{background:#10101e;border:1px solid #1a1a3e;border-radius:6px;padding:24px;margin-bottom:20px}
  table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
  th{background:#0d0d1e;padding:9px 12px;text-align:left;color:#5565a0;border-bottom:1px solid #1a1a3e;font-weight:600}
  td{padding:8px 12px;border-bottom:1px solid #1a1a3e20}
  tr:hover td{background:#ffffff05}
  .best{color:#00ffd5;font-weight:700}
  @media print{.card{break-inside:avoid}}
</style></head><body>
<h1>HappyModel — Model Comparison Report</h1>
<p class="subtitle">Dataset: <strong>${data.fileName||'—'}</strong> · Generated ${new Date().toLocaleString()} · ${comp.length} models compared</p>

<div class="card">
  <h2>Side-by-Side Metrics</h2>
  <table>
    <thead><tr><th>Metric</th>${modelHeaders}</tr></thead>
    <tbody>${metricRows}</tbody>
  </table>
  <p style="font-size:11px;color:#5565a0;margin-top:10px">★ Highlighted value = best result for that metric</p>
</div>

<h2>Per-Model Details &amp; Appendix</h2>
${modelCards}
</body></html>`;

    const blob = new Blob([html], { type: 'application/octet-stream' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `happymodel_comparison_${Date.now()}.html`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    toast('Comparison report exported!', 'success');
  } catch(err) { toast('Export failed: ' + err.message, 'error'); } };

  const actual_vs_predicted  = current.actual_vs_predicted || [];
  const residuals            = current.residuals || [];
  const feature_importances  = current.feature_importances || [];
  const roc_curve            = current.roc_curve || [];
  const pca_2d               = current.pca_2d || [];
  const learning_curve       = current.learning_curve || [];
  const lc_x_label           = current.learning_curve_x_label || 'Training Samples';

  const residualBuckets = useMemo(() => {
    if (!residuals.length) return [];
    const min = Math.min(...residuals), max = Math.max(...residuals);
    const bins = 10;
    const step = (max - min) / bins || 1;
    const counts = Array(bins).fill(0);
    residuals.forEach(r => {
      const idx = Math.min(bins - 1, Math.floor((r - min) / step));
      counts[idx]++;
    });
    return counts.map((count, i) => ({ name: (min + i * step).toFixed(2), count }));
  }, [residuals]);

  const comp = results.comparison || [];
  const primaryMetric = taskType === 'regression' ? 'r2' : taskType === 'classification' ? 'f1' : 'silhouette';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: t.text, marginBottom: 4 }}>Results</h2>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <Badge color={t.accent}>{current.modelName}</Badge>
            {current.training_time != null && (
              <Badge color="#22c55e">Training: {typeof current.training_time === 'number' ? current.training_time.toFixed(2) : current.training_time}s</Badge>
            )}
            <Badge color="#64748b">{new Date(current.timestamp).toLocaleTimeString()}</Badge>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <Button dark={dark} size="sm" variant="secondary" onClick={addToComparison}>
            + Compare {comp.length > 0 && <Badge color={t.accent}>{comp.length}</Badge>}
          </Button>
          <Button dark={dark} size="sm" variant="secondary" onClick={saveResults}>Save JSON</Button>
          <Button dark={dark} size="sm" onClick={exportReport}>Export Report</Button>
        </div>
      </div>

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 12 }}>
        {displayMetrics.map(k => <MetricCard key={k} mkey={k} value={metrics[k]} dark={dark} />)}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 20 }}>
        {/* Actual vs Predicted */}
        {actual_vs_predicted.length > 0 && (
          <Card dark={dark}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 12 }}>Actual vs Predicted</h4>
            <ResponsiveContainer width="100%" height={220}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke={t.border} />
                <XAxis dataKey="actual" name="Actual" tick={{ fill: t.muted, fontSize: 11 }} label={{ value: 'Actual', position: 'insideBottom', fill: t.muted, fontSize: 11, dy: 10 }} />
                <YAxis dataKey="predicted" name="Predicted" tick={{ fill: t.muted, fontSize: 11 }} label={{ value: 'Predicted', angle: -90, position: 'insideLeft', fill: t.muted, fontSize: 11 }} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ background: t.card, border: `1px solid ${t.border}`, borderRadius: 6, fontSize: 12 }} />
                <Scatter data={actual_vs_predicted} fill="#00ffd5" fillOpacity={0.7} />
              </ScatterChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* Residuals histogram */}
        {residualBuckets.length > 0 && (
          <Card dark={dark}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 12 }}>Residuals Distribution</h4>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={residualBuckets}>
                <CartesianGrid strokeDasharray="3 3" stroke={t.border} />
                <XAxis dataKey="name" tick={{ fill: t.muted, fontSize: 10 }} />
                <YAxis tick={{ fill: t.muted, fontSize: 11 }} />
                <Tooltip contentStyle={{ background: t.card, border: `1px solid ${t.border}`, borderRadius: 6, fontSize: 12 }} />
                <Bar dataKey="count" fill="#00ffd5" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* ROC Curve */}
        {roc_curve.length > 0 && (
          <Card dark={dark}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 12 }}>ROC Curve</h4>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={roc_curve}>
                <CartesianGrid strokeDasharray="3 3" stroke={t.border} />
                <XAxis dataKey="fpr" name="FPR" tick={{ fill: t.muted, fontSize: 11 }} label={{ value: 'False Positive Rate', position: 'insideBottom', fill: t.muted, fontSize: 11, dy: 10 }} />
                <YAxis tick={{ fill: t.muted, fontSize: 11 }} />
                <Tooltip contentStyle={{ background: t.card, border: `1px solid ${t.border}`, borderRadius: 6, fontSize: 12 }} />
                <Line type="monotone" dataKey="tpr" stroke="#00ffd5" dot={false} strokeWidth={2} name="TPR" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* Confusion Matrix */}
        {current.confusion_matrix && (
          <Card dark={dark}>
            <ConfusionMatrix matrix={current.confusion_matrix} dark={dark} />
          </Card>
        )}

        {/* Clustering scatter */}
        {pca_2d.length > 0 && (
          <Card dark={dark}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 12 }}>Cluster Visualization (PCA)</h4>
            <ResponsiveContainer width="100%" height={220}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke={t.border} />
                <XAxis dataKey="x" name="PC1" tick={{ fill: t.muted, fontSize: 11 }} />
                <YAxis dataKey="y" name="PC2" tick={{ fill: t.muted, fontSize: 11 }} />
                <Tooltip contentStyle={{ background: t.card, border: `1px solid ${t.border}`, borderRadius: 6, fontSize: 12 }} />
                <Scatter data={pca_2d} fill="#ff006e" fillOpacity={0.7} />
              </ScatterChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* Feature importances */}
        {feature_importances.length > 0 && (
          <Card dark={dark} style={{ gridColumn: 'span 2' }}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 12 }}>Feature Importances</h4>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={feature_importances.slice(0, 15)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke={t.border} />
                <XAxis type="number" tick={{ fill: t.muted, fontSize: 11 }} />
                <YAxis type="category" dataKey="feature" tick={{ fill: t.text, fontSize: 11 }} width={120} />
                <Tooltip contentStyle={{ background: t.card, border: `1px solid ${t.border}`, borderRadius: 6, fontSize: 12 }} />
                <Bar dataKey="importance" fill="#ff006e" radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* Learning / Validation Curve */}
        {learning_curve.length > 0 && (
          <Card dark={dark} style={{ gridColumn: 'span 2' }}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: t.text, marginBottom: 4 }}>
              Training vs Validation Curve
            </h4>
            <p style={{ fontSize: 11, color: t.muted, marginBottom: 12 }}>
              {lc_x_label === 'Estimators'
                ? 'Score per boosting round — if val score plateaus or drops while train score rises, the model is overfitting.'
                : 'Score vs training set size — if both scores are low the model underfit; a large gap means it overfit.'}
            </p>
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={learning_curve} margin={{ top: 4, right: 16, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={t.border} />
                <XAxis
                  dataKey="x"
                  tick={{ fill: t.muted, fontSize: 11 }}
                  label={{ value: lc_x_label, position: 'insideBottom', fill: t.muted, fontSize: 11, dy: 14 }}
                />
                <YAxis domain={['auto', 'auto']} tick={{ fill: t.muted, fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: t.card, border: `1px solid ${t.border}`, borderRadius: 6, fontSize: 12 }}
                  formatter={(v) => [typeof v === 'number' ? v.toFixed(4) : v]}
                />
                <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
                <Line type="monotone" dataKey="train_score" stroke="#00ffd5" dot={false} strokeWidth={2} name="Train" />
                <Line type="monotone" dataKey="val_score"   stroke="#ff006e" dot={false} strokeWidth={2} name="Validation" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        )}
      </div>

      {/* Model comparison panel */}
      {comp.length >= 2 && (
        <Card dark={dark}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, gap: 8, flexWrap: 'wrap' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: t.text }}>Model Comparison</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <Button dark={dark} size="sm" onClick={exportComparison}>Export Comparison</Button>
              <Button dark={dark} size="sm" variant="ghost"
                onClick={() => dispatch({ type: 'SET_RESULTS', payload: { comparison: [] } })}>
                Clear
              </Button>
            </div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: dark ? '#0f172a' : '#f8fafc' }}>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: t.muted, borderBottom: `1px solid ${t.border}`, fontWeight: 600 }}>Metric</th>
                  {comp.map((c, i) => {
                    const allVals = comp.map(x => x.metrics?.[primaryMetric] ?? null).filter(v => v !== null);
                    const best    = METRIC_INFO[primaryMetric]?.higher_better
                      ? Math.max(...allVals) : Math.min(...allVals);
                    const isBest  = c.metrics?.[primaryMetric] === best;
                    return (
                      <th key={i} style={{ padding: '10px 14px', textAlign: 'center', color: isBest ? t.accent : t.text, borderBottom: `1px solid ${t.border}`, fontWeight: 700 }}>
                        {c.modelName}
                        {isBest && <div><Badge color={t.accent}>Best Model</Badge></div>}
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {Object.keys(comp[0]?.metrics || {}).map((mkey, ri) => {
                  const vals   = comp.map(c => c.metrics?.[mkey] ?? null);
                  const numVals= vals.filter(v => v !== null && !isNaN(v));
                  const best   = numVals.length
                    ? (METRIC_INFO[mkey]?.higher_better ? Math.max(...numVals) : Math.min(...numVals))
                    : null;
                  return (
                    <tr key={mkey} style={{ background: ri % 2 === 0 ? t.card : (dark ? '#162032' : '#f8fafc') }}>
                      <td style={{ padding: '9px 14px', color: t.muted, fontWeight: 600, borderBottom: `1px solid ${t.border}33` }}>
                        {METRIC_INFO[mkey]?.label || mkey}
                      </td>
                      {vals.map((v, ci) => {
                        const isBest = v !== null && v === best;
                        return (
                          <td key={ci} style={{
                            padding: '9px 14px', textAlign: 'center',
                            fontFamily: 'DM Mono, monospace', fontSize: 14, fontWeight: isBest ? 700 : 400,
                            color: isBest ? t.accent : metricColor(mkey, v),
                            borderBottom: `1px solid ${t.border}33`,
                          }}>
                            {v !== null ? (typeof v === 'number' ? v.toFixed(4) : v) : '—'}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
// NAVBAR
// ─────────────────────────────────────────────
function Navbar({ state, dispatch }) {
  const { ui } = state;
  const dark = ui.darkMode;
  const t = tok(dark);
  const STEPS = ['Import', 'Model', 'Features', 'Params', 'Results'];

  const toggleDark = () => {
    const next = !ui.darkMode;
    dispatch({ type: 'SET_UI', payload: { darkMode: next } });
    try { localStorage.setItem('hm_dark', next ? '1' : '0'); } catch (_) {}
  };

  return (
    <header style={{
      position: 'sticky', top: 0, zIndex: 200,
      background: dark ? 'rgba(6,6,17,0.95)' : t.card,
      borderBottom: `1px solid ${dark ? '#00ffd522' : t.border}`,
      backdropFilter: 'blur(12px)',
      boxShadow: dark ? '0 2px 20px rgba(0,255,213,0.08)' : t.shadow,
      padding: '0 24px',
      display: 'flex', alignItems: 'center', height: 60, gap: 20,
    }}>
      {/* Glitch Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <span style={{ fontSize: 20, filter: 'drop-shadow(0 0 6px #00ffd5)' }}>⬡</span>
        <span className="glitch-logo" data-text="HappyModel" style={{ fontSize: 16 }}>HappyModel</span>
      </div>

      {/* Step indicator */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0 }}>
        {STEPS.map((label, i) => {
          const step = i + 1;
          const done    = step < ui.step;
          const current = step === ui.step;
          return (
            <React.Fragment key={step}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                <div style={{
                  width: 26, height: 26, borderRadius: 2,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: done ? '#00ffd522' : current ? '#00ffd511' : 'transparent',
                  color: done ? '#00ffd5' : current ? '#00ffd5' : t.muted,
                  fontSize: 11, fontWeight: 700, transition: t.trans,
                  border: `1px solid ${done || current ? '#00ffd5' : t.border}`,
                  boxShadow: current ? '0 0 8px #00ffd5, 0 0 16px rgba(0,255,213,0.3)' : 'none',
                  fontFamily: 'Share Tech Mono, monospace',
                }}>
                  {done ? <CyberIcon name="check" size={13} color="#00ffd5" /> : step}
                </div>
                <span style={{ fontSize: 9, color: current ? '#00ffd5' : t.muted, fontWeight: current ? 700 : 400, whiteSpace: 'nowrap', fontFamily: 'Share Tech Mono, monospace', letterSpacing: 0.5, textShadow: current ? '0 0 6px #00ffd5' : 'none' }}>
                  {label.toUpperCase()}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div style={{ width: 36, height: 1, background: done ? '#00ffd5' : t.border, margin: '0 4px', marginBottom: 18, transition: t.trans, boxShadow: done ? '0 0 4px #00ffd5' : 'none' }} />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Theme toggle */}
      <button onClick={toggleDark} style={{
        background: 'transparent', border: `1px solid ${t.border}`, borderRadius: 2,
        padding: '6px 10px', cursor: 'pointer', fontSize: 14, color: t.muted,
        transition: t.trans, fontFamily: 'Share Tech Mono, monospace',
      }}>
        {dark ? '[ LIGHT ]' : '[ DARK ]'}
      </button>
    </header>
  );
}

// ─────────────────────────────────────────────
// SIDEBAR
// ─────────────────────────────────────────────
const STEP_LABELS = ['Import Data', 'Select Model', 'Configure Features', 'Set Parameters', 'Results'];
const STEP_ICONS  = [
  <CyberIcon name="upload"  size={14} />,
  <CyberIcon name="cpu"     size={14} />,
  <CyberIcon name="hex"     size={14} />,
  <CyberIcon name="sliders" size={14} />,
  <CyberIcon name="chart"   size={14} />,
];

function Sidebar({ state, dispatch }) {
  const { ui } = state;
  const dark = ui.darkMode;
  const t = tok(dark);

  return (
    <aside style={{
      width: ui.sidebarOpen ? 210 : 44,
      flexShrink: 0, transition: 'width 200ms ease',
      background: dark ? 'rgba(6,6,17,0.8)' : t.card,
      borderRight: `1px solid ${dark ? '#00ffd518' : t.border}`,
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>
      <button onClick={() => dispatch({ type: 'SET_UI', payload: { sidebarOpen: !ui.sidebarOpen } })}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          padding: '10px', color: '#00ffd5', fontSize: 12, textAlign: 'right',
          fontFamily: 'Share Tech Mono, monospace', letterSpacing: 1,
        }}>
        {ui.sidebarOpen ? '◀◀' : '▶▶'}
      </button>

      <nav style={{ flex: 1, padding: '4px 0' }}>
        {STEP_LABELS.map((label, i) => {
          const step = i + 1;
          const done    = step < ui.step;
          const current = step === ui.step;
          return (
            <div key={step} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 12px', cursor: done ? 'pointer' : 'default',
              background: current ? 'rgba(0,255,213,0.06)' : 'transparent',
              borderLeft: `2px solid ${current ? '#00ffd5' : done ? '#00ffd544' : 'transparent'}`,
              boxShadow: current ? 'inset 0 0 20px rgba(0,255,213,0.03)' : 'none',
              transition: t.trans,
            }}
              onClick={() => done && dispatch({ type: 'SET_UI', payload: { step } })}>
              <span style={{
                fontSize: 13, flexShrink: 0,
                color: done ? '#39ff14' : current ? '#00ffd5' : t.muted,
                textShadow: current ? '0 0 6px #00ffd5' : done ? '0 0 4px #39ff14' : 'none',
                fontFamily: 'Share Tech Mono, monospace',
              }}>
                {done ? <CyberIcon name="check" size={13} color="#39ff14" /> : STEP_ICONS[i]}
              </span>
              {ui.sidebarOpen && (
                <span style={{
                  fontSize: 11, fontWeight: current ? 700 : 400,
                  whiteSpace: 'nowrap', letterSpacing: 0.5,
                  color: current ? '#00ffd5' : done ? t.text : t.muted,
                  textShadow: current ? '0 0 6px rgba(0,255,213,0.6)' : 'none',
                  fontFamily: 'DM Sans, sans-serif',
                }}>
                  {label}
                </span>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}

// ─────────────────────────────────────────────
// BOTTOM NAV BAR
// ─────────────────────────────────────────────
function BottomBar({ state, dispatch }) {
  const { ui, data, model, features } = state;
  const dark = ui.darkMode;
  const t = tok(dark);

  const canNext = useMemo(() => {
    if (ui.step === 1) return !!data.fileId;
    if (ui.step === 2) return !!model.id;
    if (ui.step === 3) return features.inputs.length > 0 && !!features.target;
    if (ui.step === 4) return false; // training advances step
    return false;
  }, [ui.step, data.fileId, model.id, features]);

  if (ui.step === 5) return null;

  return (
    <div style={{
      position: 'sticky', bottom: 0, zIndex: 100,
      background: dark ? 'rgba(6,6,17,0.95)' : t.card,
      backdropFilter: 'blur(12px)',
      borderTop: `1px solid ${dark ? '#00ffd518' : t.border}`,
      padding: '10px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      boxShadow: dark ? '0 -2px 20px rgba(0,255,213,0.06)' : '0 -1px 4px rgba(0,0,0,0.06)',
    }}>
      <Button dark={dark} variant="secondary" disabled={ui.step === 1}
        onClick={() => dispatch({ type: 'SET_UI', payload: { step: ui.step - 1 } })}>
        ← Back
      </Button>
      <span style={{ fontSize: 10, color: t.muted, fontFamily: 'Share Tech Mono, monospace', letterSpacing: 1 }}>
        STEP {ui.step} / 5
      </span>
      {ui.step < 4 && (
        <Button dark={dark} disabled={!canNext}
          onClick={() => dispatch({ type: 'SET_UI', payload: { step: ui.step + 1 } })}>
          Next Step →
        </Button>
      )}
      {ui.step === 4 && <div style={{ width: 120 }} />}
    </div>
  );
}

// ─────────────────────────────────────────────
// ROOT APP
// ─────────────────────────────────────────────
function AppInner() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { ui } = state;
  const dark = ui.darkMode;
  const t = tok(dark);

  // Load dark mode preference
  useEffect(() => {
    try {
      const saved = localStorage.getItem('hm_dark');
      if (saved === '1') dispatch({ type: 'SET_UI', payload: { darkMode: true } });
    } catch (_) {}
  }, []);

  // Health check
  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(r => { if (!r.ok) throw new Error(); dispatch({ type: 'SET_UI', payload: { healthOk: true } }); })
      .catch(() => dispatch({ type: 'SET_UI', payload: { healthOk: false } }));
  }, []);

  const STEPS = [StepImport, StepModel, StepFeatures, StepParams, StepResults];
  const StepComponent = STEPS[ui.step - 1] || StepImport;

  return (
    <div style={{
      minHeight: '100vh', background: t.bg, color: t.text,
      fontFamily: 'DM Sans, sans-serif', transition: t.trans,
      display: 'flex', flexDirection: 'column', position: 'relative',
    }}>
      <GlobalStyles />
      {dark && <CyberpunkBackground />}
      {dark && <CyberpunkCorners />}
      <Navbar state={state} dispatch={dispatch} />

      {/* Backend health banner */}
      {!ui.healthOk && (
        <div style={{
          background: '#ef444415', borderBottom: '1px solid #ef444433',
          padding: '10px 24px', display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <CyberIcon name="warn" size={16} color="#ef4444" />
          <span style={{ fontSize: 13, color: '#ef4444', fontWeight: 500 }}>
            Backend not running. Start it with:&nbsp;
            <code style={{ fontFamily: 'DM Mono, monospace', background: '#ef444420', padding: '2px 6px', borderRadius: 4 }}>
              python server.py
            </code>
          </span>
        </div>
      )}

      {/* Error banner */}
      {ui.error && (
        <div style={{
          background: '#ef444415', borderBottom: '1px solid #ef444433',
          padding: '10px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <span style={{ fontSize: 13, color: '#ef4444' }}>Error: {ui.error}</span>
          <button onClick={() => dispatch({ type: 'SET_UI', payload: { error: null } })}
            style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: 0, display: 'flex' }}><CyberIcon name="close" size={16} color="#ef4444" /></button>
        </div>
      )}

      <div style={{ display: 'flex', flex: 1, minHeight: 0, position: 'relative', zIndex: 1 }}>
        <Sidebar state={state} dispatch={dispatch} />
        <main style={{ flex: 1, overflow: 'auto', padding: 28, minWidth: 0 }}>
          <StepComponent state={state} dispatch={dispatch} />
        </main>
      </div>

      <BottomBar state={state} dispatch={dispatch} />
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppInner />
    </ToastProvider>
  );
}
