# Trainr – Setup Guide

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.8+ | `python --version` |
| pip | 21+ | `pip --version` |
| Node.js | 16+ | `node --version` |
| npm | 8+ | `npm --version` |

---

## Quick Start (2 terminals)

### Terminal 1 — Backend

```bash
cd trainr/backend
pip install -r requirements.txt
python server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 — Frontend

```bash
cd trainr/frontend
npm install
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in 300ms
  ➜  Local:   http://localhost:5173/
```

Open your browser at **http://localhost:5173**

---

## Verifying the Setup

1. Visit `http://localhost:8000/health` in your browser
   - Should return: `{"status": "ok"}`
2. Visit `http://localhost:5173`
   - Should show Trainr with a green health status
   - If you see "Backend not running" banner → make sure Terminal 1 is running

---

## Optional: Deep Learning (TensorFlow)

TensorFlow is **not required**. Deep learning models (MLP, LSTM, CNN-1D, Autoencoder) are only available if installed.

```bash
pip install tensorflow
```

> ⚠️ TensorFlow requires Python 3.8–3.11. It may need additional GPU setup for hardware acceleration.

---

## Optional: Prophet (Time Series)

```bash
pip install prophet
```

---

## Troubleshooting

### Port already in use
```bash
# Find what's using port 8000 (macOS/Linux)
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Kill process (replace PID)
kill -9 <PID>     # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### pip install fails
Try using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### npm install fails
```bash
# Clear npm cache
npm cache clean --force
npm install
```

### CORS errors in browser console
- Ensure backend is running at `http://localhost:8000`
- Ensure frontend is running at `http://localhost:5173` or `http://localhost:3000`
- Both are already allowed in CORS config

### XGBoost errors on Apple Silicon (M1/M2)
```bash
pip install xgboost --no-binary xgboost
```

---

## File Upload Limits

- Default max file size: ~100MB (limited by server memory)
- For large files (>50MB), increase uvicorn timeout in `server.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=120)
  ```

---

## Project Structure

```
trainr/
├── backend/
│   ├── server.py           # Run this first
│   ├── requirements.txt
│   └── start.sh
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Full React app
│   │   └── main.jsx        # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── API_SPECIFICATION.md
│   ├── MODEL_REFERENCE.md
│   └── SETUP_GUIDE.md      # This file
└── README.md
```

---

## Sample Workflow

1. **Start both servers** (see Quick Start above)
2. **Upload a CSV** — try the sample file at `docs/sample_data.csv`
3. **Select a model** — try XGBoost Classifier or Random Forest Regressor
4. **Pick features** — check any columns, set target column
5. **Set parameters** — use "Balanced" preset for a good start
6. **Train** — click "Train Model" and wait a few seconds
7. **View results** — explore metrics, charts, and feature importance

---

## Development Notes

- The backend auto-reloads on file changes if you run with `--reload`:
  ```bash
  uvicorn server:app --reload --port 8000
  ```
- The frontend hot-reloads automatically via Vite

---

## Windows-Specific Notes

- Use PowerShell or Git Bash
- If `python` is not found, try `python3` or `py`
- File paths use backslashes — all commands above work in Git Bash with forward slashes
