"""
HappyModel — Cyberpunk ML Studio
A no-code machine learning desktop application built with PyQt5.
Connects to the FastAPI backend at http://localhost:8000
"""

import sys
import os
import json
import time
from datetime import datetime
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QComboBox, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QStackedWidget, QFrame, QScrollArea, QGridLayout, QSplitter,
    QProgressBar, QMessageBox, QHeaderView, QSizePolicy, QTabWidget,
    QTabBar, QToolTip, QStatusBar, QSpacerItem
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QPoint
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QFontDatabase, QIcon, QPainter,
    QLinearGradient, QBrush, QPen, QPixmap
)

import requests
import numpy as np

# Matplotlib with Qt backend
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ═══════════════════════════════════════════════════════════
# CYBERPUNK COLOR PALETTE
# ═══════════════════════════════════════════════════════════
C = {
    'bg':          '#0a0a0f',
    'panel':       '#12121a',
    'card':        '#16162a',
    'card_hover':  '#1a1a2e',
    'border':      '#1e1e3a',
    'cyan':        '#00ffd5',
    'magenta':     '#ff006e',
    'blue':        '#4361ee',
    'green':       '#39ff14',
    'amber':       '#ffbe0b',
    'purple':      '#b829dd',
    'text':        '#e0e0ff',
    'muted':       '#6a6a8a',
    'input_bg':    '#0d0d15',
    'input_border':'#2a2a4a',
    'dim':         '#333355',
}

API_BASE = 'http://localhost:8000'

# ═══════════════════════════════════════════════════════════
# GLOBAL STYLESHEET
# ═══════════════════════════════════════════════════════════
STYLESHEET = f"""
QMainWindow {{
    background-color: {C['bg']};
}}
QWidget {{
    background-color: transparent;
    color: {C['text']};
    font-family: Consolas, 'Courier New', monospace;
    font-size: 16px;
}}
QLabel {{
    color: {C['text']};
    background: transparent;
}}
QLabel#heading {{
    font-size: 26px;
    font-weight: bold;
    color: {C['cyan']};
}}
QLabel#subheading {{
    font-size: 16px;
    color: {C['muted']};
}}
QLabel#metric {{
    font-size: 28px;
    font-weight: bold;
    color: {C['cyan']};
    font-family: Consolas, monospace;
}}
QLabel#metric_label {{
    font-size: 11px;
    font-weight: bold;
    color: {C['muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}
QLabel#neon {{
    color: {C['cyan']};
    font-weight: bold;
}}
QPushButton {{
    background-color: {C['panel']};
    color: #e0e0ff;
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 12px 28px;
    font-size: 16px;
    font-weight: bold;
    font-family: Consolas, monospace;
}}
QPushButton:hover {{
    border: 1px solid {C['cyan']};
    background-color: {C['card']};
    color: #e0e0ff;
}}
QPushButton:pressed {{
    background-color: {C['cyan']};
    color: {C['bg']};
}}
QPushButton:disabled {{
    color: {C['dim']};
    border-color: {C['dim']};
}}
QPushButton#primary {{
    background-color: {C['cyan']};
    color: {C['bg']};
    border: none;
    padding: 16px 44px;
    font-size: 19px;
    font-weight: bold;
    border-radius: 8px;
}}
QPushButton#primary:hover {{
    background-color: #33ffe0;
    color: {C['bg']};
}}
QPushButton#primary:pressed {{
    background-color: #00ccaa;
    color: {C['bg']};
}}
QPushButton#primary:disabled {{
    background-color: {C['dim']};
    color: {C['muted']};
}}
QPushButton#danger {{
    border-color: {C['magenta']};
    color: {C['magenta']};
}}
QPushButton#danger:hover {{
    background-color: {C['magenta']};
    color: {C['bg']};
}}
QPushButton#preset {{
    padding: 6px 14px;
    font-size: 11px;
    border-radius: 4px;
    color: #e0e0ff;
}}
QPushButton#step_btn {{
    background-color: transparent;
    border: none;
    color: #a0a0cc;
    text-align: left;
    padding: 16px 22px;
    font-size: 16px;
    border-left: 3px solid transparent;
    border-radius: 0;
}}
QPushButton#step_btn:hover {{
    color: {C['text']};
    background-color: {C['card']};
}}
QPushButton#step_active {{
    background-color: {C['card']};
    border: none;
    color: {C['cyan']};
    text-align: left;
    padding: 16px 22px;
    font-size: 16px;
    border-left: 3px solid {C['cyan']};
    border-radius: 0;
    font-weight: bold;
}}
QComboBox {{
    background-color: {C['input_bg']};
    color: {C['text']};
    border: 1px solid {C['input_border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 16px;
    font-family: Consolas, monospace;
    min-height: 38px;
}}
QComboBox:focus {{
    border: 1px solid {C['cyan']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {C['panel']};
    color: {C['text']};
    border: 1px solid {C['border']};
    selection-background-color: {C['card']};
    selection-color: {C['cyan']};
    outline: none;
}}
QSpinBox, QDoubleSpinBox {{
    background-color: {C['input_bg']};
    color: {C['text']};
    border: 1px solid {C['input_border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-family: Consolas, monospace;
    font-size: 16px;
    min-height: 38px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {C['cyan']};
}}
QSlider::groove:horizontal {{
    height: 4px;
    background: {C['input_border']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 16px;
    height: 16px;
    margin: -6px 0;
    background: {C['cyan']};
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {C['cyan']};
    border-radius: 2px;
}}
QCheckBox {{
    color: {C['text']};
    spacing: 8px;
    font-size: 16px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {C['input_border']};
    border-radius: 4px;
    background: {C['input_bg']};
}}
QCheckBox::indicator:checked {{
    background: {C['cyan']};
    border-color: {C['cyan']};
}}
QCheckBox::indicator:hover {{
    border-color: {C['cyan']};
}}
QGroupBox {{
    border: 1px solid {C['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding: 20px 16px 12px 16px;
    font-weight: bold;
    font-size: 15px;
    color: {C['cyan']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {C['cyan']};
    font-size: 15px;
}}
QTableWidget {{
    background-color: {C['panel']};
    alternate-background-color: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    gridline-color: {C['border']};
    color: {C['text']};
    font-family: Consolas, monospace;
    font-size: 14px;
    selection-background-color: {C['card_hover']};
    selection-color: {C['cyan']};
}}
QTableWidget::item {{
    padding: 4px 8px;
}}
QHeaderView::section {{
    background-color: {C['bg']};
    color: {C['muted']};
    border: none;
    border-bottom: 2px solid {C['border']};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
}}
QTabWidget::pane {{
    border: 1px solid {C['border']};
    border-top: none;
    background: {C['panel']};
    border-radius: 0 0 8px 8px;
}}
QTabBar::tab {{
    background: {C['bg']};
    color: {C['muted']};
    border: 1px solid {C['border']};
    border-bottom: none;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 15px;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
}}
QTabBar::tab:selected {{
    background: {C['panel']};
    color: {C['cyan']};
    border-bottom: 2px solid {C['cyan']};
}}
QTabBar::tab:hover:!selected {{
    color: {C['text']};
    background: {C['card']};
}}
QScrollBar:vertical {{
    background: {C['bg']};
    width: 8px;
    border: none;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {C['dim']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C['cyan']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {C['bg']};
    height: 8px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C['dim']};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {C['cyan']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QProgressBar {{
    background: {C['input_bg']};
    border: 1px solid {C['border']};
    border-radius: 4px;
    text-align: center;
    color: {C['text']};
    font-size: 11px;
    height: 20px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {C['cyan']}, stop:1 {C['blue']});
    border-radius: 3px;
}}
QToolTip {{
    background-color: {C['card']};
    color: {C['text']};
    border: 1px solid {C['cyan']};
    padding: 6px 10px;
    font-size: 12px;
    border-radius: 4px;
}}
QStatusBar {{
    background: {C['panel']};
    color: {C['muted']};
    border-top: 1px solid {C['border']};
    font-size: 14px;
}}
QFrame#card {{
    background-color: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 8px;
}}
QFrame#card:hover {{
    border-color: {C['cyan']};
}}
QFrame#card_selected {{
    background-color: {C['card']};
    border: 2px solid {C['cyan']};
    border-radius: 8px;
}}
QFrame#separator {{
    background-color: {C['border']};
    max-height: 1px;
}}
"""

# ═══════════════════════════════════════════════════════════
# MODEL CATALOG
# ═══════════════════════════════════════════════════════════
MODEL_CATALOG = {
    'Regression': [
        {'id': 'linear_regression',           'name': 'Linear Regression',           'complexity': 'Low',  'desc': 'Fits a straight line. Fast and interpretable.'},
        {'id': 'ridge',                       'name': 'Ridge Regression',            'complexity': 'Low',  'desc': 'Linear regression with L2 regularization.'},
        {'id': 'lasso',                       'name': 'Lasso Regression',            'complexity': 'Low',  'desc': 'Linear regression with L1 regularization. Feature selection.'},
        {'id': 'random_forest_regressor',     'name': 'Random Forest Regressor',     'complexity': 'Med',  'desc': 'Ensemble of decision trees. Robust and versatile.'},
        {'id': 'xgboost_regressor',           'name': 'XGBoost Regressor',           'complexity': 'High', 'desc': 'Gradient boosted trees. State-of-the-art performance.'},
        {'id': 'gradient_boosting_regressor', 'name': 'Gradient Boosting Regressor', 'complexity': 'Med',  'desc': 'Sequential ensemble. Highly accurate.'},
        {'id': 'svr',                         'name': 'Support Vector Regressor',    'complexity': 'Med',  'desc': 'Finds optimal hyperplane with max margin.'},
    ],
    'Classification': [
        {'id': 'logistic_regression',          'name': 'Logistic Regression',          'complexity': 'Low',  'desc': 'Linear classifier with probability outputs.'},
        {'id': 'random_forest_classifier',     'name': 'Random Forest Classifier',     'complexity': 'Med',  'desc': 'Ensemble of decision trees for classification.'},
        {'id': 'xgboost_classifier',           'name': 'XGBoost Classifier',           'complexity': 'High', 'desc': 'Gradient boosted trees. Excellent accuracy.'},
        {'id': 'svm_classifier',               'name': 'SVM Classifier',               'complexity': 'Med',  'desc': 'Finds separating hyperplane. High-dimensional data.'},
        {'id': 'knn',                          'name': 'K-Nearest Neighbors',          'complexity': 'Low',  'desc': 'Classifies by nearest neighbor voting.'},
        {'id': 'naive_bayes',                  'name': 'Naive Bayes',                  'complexity': 'Low',  'desc': 'Probabilistic classifier. Very fast.'},
        {'id': 'gradient_boosting_classifier', 'name': 'Gradient Boosting Classifier', 'complexity': 'Med',  'desc': 'Sequential ensemble for classification.'},
    ],
    'Clustering': [
        {'id': 'kmeans',       'name': 'K-Means',                  'complexity': 'Low',  'desc': 'Partitions data into k clusters by centroids.'},
        {'id': 'dbscan',       'name': 'DBSCAN',                   'complexity': 'Med',  'desc': 'Density-based. Finds arbitrary-shaped clusters.'},
        {'id': 'hierarchical', 'name': 'Hierarchical Clustering',  'complexity': 'Med',  'desc': 'Builds cluster dendrogram bottom-up.'},
    ],
    'Statistical': [
        {'id': 'arima',                  'name': 'ARIMA',                  'complexity': 'Med',  'desc': 'Classic time series model for stationary data.'},
        {'id': 'sarima',                 'name': 'SARIMA',                 'complexity': 'High', 'desc': 'Seasonal ARIMA for periodic patterns.'},
        {'id': 'exponential_smoothing',  'name': 'Exponential Smoothing',  'complexity': 'Low',  'desc': 'Weighted average of past observations.'},
    ],
    'Deep Learning': [
        {'id': 'mlp',         'name': 'Multi-Layer Perceptron', 'complexity': 'High', 'desc': 'Fully connected neural network.'},
        {'id': 'lstm',        'name': 'LSTM',                   'complexity': 'High', 'desc': 'Recurrent network for sequences.'},
        {'id': 'cnn_1d',      'name': 'CNN-1D',                 'complexity': 'High', 'desc': '1D convolution for signal/sequence data.'},
        {'id': 'autoencoder', 'name': 'Autoencoder',            'complexity': 'High', 'desc': 'Unsupervised. Learns compressed representation.'},
    ],
}

DEFAULT_PARAMS = {
    'linear_regression': {},
    'ridge': {'alpha': 1.0},
    'lasso': {'alpha': 1.0},
    'random_forest_regressor': {'n_estimators': 100, 'max_depth': 10, 'min_samples_split': 2},
    'random_forest_classifier': {'n_estimators': 100, 'max_depth': 10, 'min_samples_split': 2},
    'xgboost_regressor': {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 5, 'subsample': 1.0, 'colsample_bytree': 1.0},
    'xgboost_classifier': {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 5, 'subsample': 1.0, 'colsample_bytree': 1.0},
    'gradient_boosting_regressor': {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 3},
    'gradient_boosting_classifier': {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 3},
    'logistic_regression': {'C': 1.0, 'max_iter': 1000},
    'svm_classifier': {'C': 1.0, 'kernel': 'rbf'},
    'svr': {'C': 1.0, 'kernel': 'rbf'},
    'knn': {'n_neighbors': 5},
    'naive_bayes': {},
    'kmeans': {'n_clusters': 3},
    'dbscan': {'eps': 0.5, 'min_samples': 5},
    'hierarchical': {'n_clusters': 3},
    'arima': {'p': 1, 'd': 1, 'q': 1},
    'sarima': {'p': 1, 'd': 1, 'q': 1, 'P': 1, 'D': 1, 'Q': 1, 'm': 12},
    'exponential_smoothing': {},
    'mlp': {'units': 64, 'layers': 2, 'dropout': 0.2, 'epochs': 50, 'batch_size': 32, 'learning_rate': 0.001},
    'lstm': {'units': 64, 'layers': 2, 'dropout': 0.2, 'epochs': 50, 'batch_size': 32, 'learning_rate': 0.001},
    'cnn_1d': {'units': 64, 'layers': 2, 'dropout': 0.2, 'epochs': 50, 'batch_size': 32, 'learning_rate': 0.001},
    'autoencoder': {'units': 64, 'layers': 2, 'dropout': 0.2, 'epochs': 50, 'batch_size': 32, 'learning_rate': 0.001},
}

PRESETS = {
    'Conservative': {'n_estimators': 50, 'max_depth': 3, 'learning_rate': 0.01, 'epochs': 20, 'dropout': 0.3},
    'Balanced':     {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'epochs': 50, 'dropout': 0.2},
    'Aggressive':   {'n_estimators': 300, 'max_depth': 12, 'learning_rate': 0.2, 'epochs': 150, 'dropout': 0.1},
}

# ═══════════════════════════════════════════════════════════
# WORKER THREADS
# ═══════════════════════════════════════════════════════════
class UploadWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            with open(self.filepath, 'rb') as f:
                files = {'file': (os.path.basename(self.filepath), f)}
                resp = requests.post(f'{API_BASE}/upload', files=files, timeout=60)
            if resp.status_code != 200:
                self.error.emit(f"Upload failed: {resp.text}")
                return
            self.finished.emit(resp.json())
        except Exception as e:
            self.error.emit(str(e))


class TrainWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, body):
        super().__init__()
        self.body = body

    def run(self):
        try:
            resp = requests.post(f'{API_BASE}/train', json=self.body, timeout=300)
            if resp.status_code != 200:
                detail = resp.json().get('detail', resp.text)
                self.error.emit(f"Training failed: {detail}")
                return
            self.finished.emit(resp.json())
        except Exception as e:
            self.error.emit(str(e))


# ═══════════════════════════════════════════════════════════
# HELPER WIDGETS
# ═══════════════════════════════════════════════════════════
def make_card(parent=None):
    frame = QFrame(parent)
    frame.setObjectName('card')
    return frame

def make_selected_card(parent=None):
    frame = QFrame(parent)
    frame.setObjectName('card_selected')
    return frame

def neon_label(text, color=None, size=16, bold=False, parent=None):
    lbl = QLabel(text, parent)
    c = color or C['cyan']
    weight = 'bold' if bold else 'normal'
    lbl.setStyleSheet(f"color: {c}; font-size: {size}px; font-weight: {weight}; background: transparent;")
    return lbl

def muted_label(text, size=15, parent=None):
    lbl = QLabel(text, parent)
    lbl.setStyleSheet(f"color: {C['muted']}; font-size: {size}px; background: transparent;")
    return lbl

def heading_label(text, parent=None):
    lbl = QLabel(text, parent)
    lbl.setObjectName('heading')
    return lbl

def separator(parent=None):
    line = QFrame(parent)
    line.setObjectName('separator')
    line.setFixedHeight(1)
    return line

def badge_label(text, color, parent=None):
    lbl = QLabel(f"  {text}  ", parent)
    lbl.setStyleSheet(f"""
        background-color: {color}22;
        color: {color};
        border: 1px solid {color}55;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
    """)
    lbl.setFixedHeight(22)
    return lbl

def make_scroll_area(widget):
    scroll = QScrollArea()
    scroll.setWidget(widget)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setStyleSheet(f"background: {C['bg']};")
    return scroll


# ═══════════════════════════════════════════════════════════
# MATPLOTLIB CYBERPUNK CHART HELPER
# ═══════════════════════════════════════════════════════════
class CyberChart(FigureCanvas):
    def __init__(self, width=5, height=4, parent=None):
        self.fig = Figure(figsize=(width, height), facecolor=C['bg'], edgecolor=C['border'])
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self._style_ax(self.ax)

    def _style_ax(self, ax):
        ax.set_facecolor(C['panel'])
        ax.tick_params(colors=C['muted'], labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(C['border'])
        ax.spines['bottom'].set_color(C['border'])
        ax.xaxis.label.set_color(C['muted'])
        ax.yaxis.label.set_color(C['muted'])
        ax.title.set_color(C['cyan'])
        ax.title.set_fontsize(12)
        ax.title.set_fontweight('bold')
        ax.grid(True, color=C['border'], alpha=0.3, linestyle='--')

    def clear_and_style(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self._style_ax(self.ax)
        return self.ax


# ═══════════════════════════════════════════════════════════
# ANIMATED CYBERPUNK CORNER DECORATIONS
# ═══════════════════════════════════════════════════════════
class CyberpunkCorners(QWidget):
    """Animated neon corner decorations drawn with QPainter."""

    GLYPHS = ['◈', '⬡', '◉', '▣', '◫', '⬢', '◈', '⟁', '⬟', '◧']
    CIRCUIT_CHARS = ['┤', '├', '┬', '┴', '┼', '╔', '╗', '╚', '╝', '═', '║']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Don't block clicks
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setStyleSheet("background: transparent;")

        self.tick = 0
        self.glyph_states = []
        for i in range(8):
            self.glyph_states.append({
                'char': self.GLYPHS[i % len(self.GLYPHS)],
                'alpha': float(i * 30 % 200 + 55),
                'pulse_offset': i * 0.4,
            })

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(60)  # ~16fps

    def _tick(self):
        self.tick += 1
        # Cycle glyphs occasionally
        if self.tick % 45 == 0:
            import random
            idx = random.randint(0, len(self.glyph_states) - 1)
            self.glyph_states[idx]['char'] = self.GLYPHS[random.randint(0, len(self.GLYPHS) - 1)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        import math
        w, h = self.width(), self.height()
        t = self.tick

        # Pulse function
        def pulse(offset=0, speed=1):
            return 0.5 + 0.5 * math.sin((t * speed * 0.05) + offset)

        def draw_corner(cx, cy, flip_x, flip_y, glyph_list):
            """Draw a neon corner bracket with glyphs."""
            sx = 1 if not flip_x else -1
            sy = 1 if not flip_y else -1
            size = 80  # bracket size

            # Corner bracket lines
            alpha_base = int(120 + 80 * pulse(cx * 0.01))

            # Outer L bracket
            pen = QPen(QColor(0, 255, 213, alpha_base))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(cx, cy, cx + sx * size, cy)
            painter.drawLine(cx, cy, cx, cy + sy * size)

            # Inner corner accent
            pen2 = QPen(QColor(255, 0, 110, int(alpha_base * 0.6)))
            pen2.setWidth(1)
            painter.setPen(pen2)
            offset = 6
            painter.drawLine(cx + sx * offset, cy + sy * offset, cx + sx * (size - 20), cy + sy * offset)
            painter.drawLine(cx + sx * offset, cy + sy * offset, cx + sx * offset, cy + sy * (size - 20))

            # Glyphs along the bracket
            font = QFont("Consolas", 13)
            font.setBold(True)
            painter.setFont(font)

            for i, gs in enumerate(glyph_list):
                angle_alpha = int(80 + 120 * pulse(gs['pulse_offset'], 0.8))
                painter.setPen(QColor(0, 255, 213, angle_alpha))
                gx = cx + sx * (18 + i * 22)
                gy = cy + sy * 22
                painter.drawText(gx - 8, gy + 6, gs['char'])

                # Vertical glyph
                painter.setPen(QColor(180, 41, 221, int(angle_alpha * 0.7)))
                gx2 = cx + sx * 22
                gy2 = cy + sy * (18 + i * 22)
                painter.drawText(gx2 - 8, gy2 + 6, self.CIRCUIT_CHARS[i % len(self.CIRCUIT_CHARS)])

            # Dot at corner tip
            dot_alpha = int(180 + 75 * pulse(cx * 0.02, 1.5))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 255, 213, dot_alpha))
            painter.drawEllipse(cx - sx * 2, cy - sy * 2, 5, 5)

        # Scanline effect (subtle horizontal lines across full width)
        scan_alpha = int(8 + 6 * pulse(0, 0.3))
        pen_scan = QPen(QColor(0, 255, 213, scan_alpha))
        pen_scan.setWidth(1)
        painter.setPen(pen_scan)
        scan_y = (t * 2) % h
        for dy in range(0, h, 6):
            y = (scan_y + dy) % h
            painter.drawLine(0, y, w, y)

        gs = self.glyph_states
        margin = 16

        # Top-left corner
        draw_corner(margin, margin, False, False, gs[0:3])
        # Top-right corner
        draw_corner(w - margin, margin, True, False, gs[2:5])
        # Bottom-left corner
        draw_corner(margin, h - margin, False, True, gs[4:7])
        # Bottom-right corner
        draw_corner(w - margin, h - margin, True, True, gs[5:8])

        painter.end()


# ═══════════════════════════════════════════════════════════
# STEP 1 — IMPORT DATA
# ═══════════════════════════════════════════════════════════
class StepImport(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.worker = None
        self.setAcceptDrops(True)
        self.init_ui()

    def _drop_default_style(self):
        return (
            f"QFrame {{ border: 2px dashed {C['dim']}; border-radius: 16px; "
            f"background: {C['panel']}; min-height: 220px; }} "
            f"QFrame:hover {{ border-color: {C['cyan']}; background: {C['card']}; }}"
        )

    def _drop_hover_style(self):
        return (
            f"QFrame {{ border: 2px solid {C['cyan']}; border-radius: 16px; "
            f"background: {C['card_hover']}; min-height: 220px; }}"
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_frame.setStyleSheet(self._drop_hover_style())

    def dragLeaveEvent(self, event):
        self.drop_frame.setStyleSheet(self._drop_default_style())

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.drop_frame.setStyleSheet(self._drop_default_style())
            self.upload_file(path)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(heading_label("// IMPORT DATA"))
        layout.addWidget(muted_label("Upload your dataset to initialize the pipeline."))
        layout.addSpacing(8)

        # Drop zone — stored as class attribute for drag/drop style updates
        self.drop_frame = QFrame()
        self.drop_frame.setStyleSheet(self._drop_default_style())
        self.drop_frame.setCursor(Qt.PointingHandCursor)
        self.drop_frame.mousePressEvent = lambda event: self.browse_file()

        drop_layout = QVBoxLayout(self.drop_frame)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(14)

        icon_lbl = QLabel("📂")
        icon_lbl.setStyleSheet("font-size: 64px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(icon_lbl)

        drop_layout.addWidget(neon_label("Drag & Drop your file here", C['text'], 18, True))
        drop_layout.addWidget(muted_label("or click the button below", 15))

        # Format chips row
        chips_row = QHBoxLayout()
        chips_row.setAlignment(Qt.AlignCenter)
        chips_row.setSpacing(8)
        format_chips = [
            ('CSV', C['cyan']),
            ('Excel', C['green']),
            ('Parquet', C['blue']),
            ('JSON', C['amber']),
            ('TXT', C['purple']),
        ]
        for fmt, color in format_chips:
            chip = QLabel(fmt)
            chip.setStyleSheet(f"""
                background-color: {color}22;
                color: {color};
                border: 1px solid {color}55;
                border-radius: 4px;
                padding: 3px 10px;
                font-size: 13px;
                font-weight: bold;
            """)
            chip.setFixedHeight(26)
            chips_row.addWidget(chip)
        drop_layout.addLayout(chips_row)

        drop_layout.addSpacing(6)

        self.btn_browse = QPushButton("📂  BROWSE FILES")
        self.btn_browse.setObjectName('primary')
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self.browse_file)
        # Prevent the browse button click from also triggering the frame click
        self.btn_browse.mousePressEvent = lambda event: (
            event.accept(),
            self.browse_file()
        )
        drop_layout.addWidget(self.btn_browse, alignment=Qt.AlignCenter)

        layout.addWidget(self.drop_frame)

        # Progress bar (hidden by default)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setFixedHeight(20)
        self.progress.setVisible(False)
        self.progress_label = muted_label("Processing file...")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress)

        # Results area
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(12)
        self.results_widget.setVisible(False)
        layout.addWidget(self.results_widget)

        layout.addStretch()

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "",
            "Data Files (*.csv *.xlsx *.xls *.parquet *.json *.txt);;All Files (*)"
        )
        if path:
            self.upload_file(path)

    def upload_file(self, path):
        self.progress.setVisible(True)
        self.progress_label.setVisible(True)
        self.results_widget.setVisible(False)
        self.btn_browse.setEnabled(False)

        self.worker = UploadWorker(path)
        self.worker.finished.connect(self.on_upload_success)
        self.worker.error.connect(self.on_upload_error)
        self.worker.start()

    def on_upload_success(self, data):
        self.progress.setVisible(False)
        self.progress_label.setVisible(False)
        self.btn_browse.setEnabled(True)

        self.state['file_id'] = data.get('file_id')
        self.state['filename'] = data.get('filename', '?')
        self.state['columns'] = data.get('columns', [])
        self.state['types'] = data.get('inferred_types', {})
        self.state['preview'] = data.get('preview', [])
        self.state['shape'] = data.get('shape', {})
        self.state['stats'] = data.get('stats', {})

        self.show_results()
        main = self.window()
        if hasattr(main, 'update_sidebar'):
            main.update_sidebar()
            main.statusBar().showMessage(f"✓ Loaded {self.state['filename']}  —  {self.state['shape'].get('rows', 0)} rows × {self.state['shape'].get('cols', 0)} cols")

    def on_upload_error(self, msg):
        self.progress.setVisible(False)
        self.progress_label.setVisible(False)
        self.btn_browse.setEnabled(True)
        QMessageBox.critical(self, "Upload Error", msg)

    def show_results(self):
        # Clear previous
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        s = self.state
        # File summary card
        card = make_card()
        cl = QHBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        info_layout = QVBoxLayout()
        info_layout.addWidget(neon_label(s['filename'], C['text'], 15, True))
        info_layout.addWidget(muted_label(
            f"{s['shape'].get('rows', 0):,} rows  ×  {s['shape'].get('cols', 0)} columns"
        ))
        cl.addLayout(info_layout, 1)
        cl.addWidget(badge_label("LOADED", C['green']))
        self.results_layout.addWidget(card)

        # Column cards grid
        self.results_layout.addWidget(neon_label(f"Columns ({len(s['columns'])})", C['cyan'], 17, True))

        TYPE_COLORS = {'numeric': C['blue'], 'categorical': C['purple'], 'datetime': C['amber'], 'text': C['muted']}
        TYPE_ICONS = {'numeric': '🔢', 'categorical': '🔤', 'datetime': '📅', 'text': '📝'}

        cols_grid = QGridLayout()
        cols_grid.setSpacing(8)
        for i, col in enumerate(s['columns']):
            cname = col['name']
            dtype = s['types'].get(cname, 'text')
            tcolor = TYPE_COLORS.get(dtype, C['muted'])

            cframe = make_card()
            cframe.setStyleSheet(f"""
                QFrame {{
                    background: {C['card']};
                    border: 1px solid {C['border']};
                    border-left: 3px solid {tcolor};
                    border-radius: 6px;
                    padding: 0;
                    min-height: 100px;
                }}
                QFrame:hover {{ border-color: {tcolor}; }}
            """)
            cfl = QVBoxLayout(cframe)
            cfl.setContentsMargins(12, 16, 12, 16)
            cfl.setSpacing(6)

            cfl.addWidget(neon_label(cname, C['text'], 15, True))

            badge_row = QHBoxLayout()
            badge_row.addWidget(badge_label(f"{TYPE_ICONS.get(dtype, '')} {dtype}", tcolor))
            badge_row.addStretch()
            cfl.addLayout(badge_row)

            null_pct = f"{(col['null_count'] / max(s['shape'].get('rows', 1), 1) * 100):.1f}" if col.get('null_count') else '0.0'
            cfl.addWidget(muted_label(f"{col.get('unique_count', '?')} unique  ·  {null_pct}% null", 13))

            row, colp = divmod(i, 3)
            cols_grid.addWidget(cframe, row, colp)

        cols_w = QWidget()
        cols_w.setLayout(cols_grid)
        self.results_layout.addWidget(cols_w)

        # Preview table
        if s['preview']:
            self.results_layout.addWidget(neon_label("Data Preview (first 10 rows)", C['cyan'], 17, True))
            col_names = [c['name'] for c in s['columns']]
            table = QTableWidget(min(10, len(s['preview'])), len(col_names))
            table.setHorizontalHeaderLabels(col_names)
            table.horizontalHeader().setStretchLastSection(True)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setMinimumHeight(280)

            for ri, row in enumerate(s['preview'][:10]):
                for ci, cn in enumerate(col_names):
                    item = QTableWidgetItem(str(row.get(cn, '')))
                    item.setForeground(QColor(C['text']))
                    table.setItem(ri, ci, item)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.results_layout.addWidget(table)

        self.results_widget.setVisible(True)


# ═══════════════════════════════════════════════════════════
# STEP 2 — SELECT MODEL
# ═══════════════════════════════════════════════════════════
class StepModel(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.selected_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(heading_label("// SELECT MODEL"))
        layout.addWidget(muted_label("Choose a machine learning algorithm for your task."))
        layout.addSpacing(4)

        # Recommendation banner
        self.rec_banner = QFrame()
        self.rec_banner.setStyleSheet(f"""
            QFrame {{
                background: {C['cyan']}11;
                border: 1px solid {C['cyan']}44;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        rec_layout = QHBoxLayout(self.rec_banner)
        rec_layout.setContentsMargins(14, 10, 14, 10)
        self.rec_label = neon_label("⚡ Recommendation will appear after data upload", C['cyan'], 15)
        rec_layout.addWidget(self.rec_label)
        layout.addWidget(self.rec_banner)

        # Tabs
        self.tabs = QTabWidget()
        self.model_cards = {}

        for cat, models in MODEL_CATALOG.items():
            page = QWidget()
            grid = QGridLayout(page)
            grid.setSpacing(10)
            grid.setContentsMargins(12, 12, 12, 12)

            for i, m in enumerate(models):
                card = self._make_model_card(m, cat)
                row, col = divmod(i, 3)
                grid.addWidget(card, row, col)

            grid.setRowStretch(grid.rowCount(), 1)
            scroll = make_scroll_area(page)
            self.tabs.addTab(scroll, cat)

        layout.addWidget(self.tabs, 1)

    def _make_model_card(self, model, category):
        mid = model['id']
        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedHeight(140)
        card.setMinimumWidth(200)

        style_default = f"""
            QFrame {{
                background: {C['card']};
                border: 1px solid {C['border']};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {C['cyan']};
            }}
        """
        style_selected = f"""
            QFrame {{
                background: {C['card_hover']};
                border: 2px solid {C['cyan']};
                border-radius: 8px;
            }}
        """
        card.setStyleSheet(style_default)
        card.setProperty('style_default', style_default)
        card.setProperty('style_selected', style_selected)
        card.setProperty('model_id', mid)
        card.setProperty('model_data', model)
        card.setProperty('category', category)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(6)

        name_row = QHBoxLayout()
        name_row.addWidget(neon_label(model['name'], C['text'], 13, True))
        name_row.addStretch()

        comp_colors = {'Low': C['green'], 'Med': C['amber'], 'High': C['magenta']}
        name_row.addWidget(badge_label(model['complexity'], comp_colors.get(model['complexity'], C['muted'])))
        cl.addLayout(name_row)

        desc = QLabel(model['desc'])
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {C['muted']}; font-size: 11px; background: transparent;")
        cl.addWidget(desc)
        cl.addStretch()

        self.model_cards[mid] = card
        card.mousePressEvent = partial(self._select_model, mid, model, category)

        return card

    def _select_model(self, mid, model, category, event=None):
        # Deselect all
        for cid, card in self.model_cards.items():
            card.setStyleSheet(card.property('style_default'))

        # Select this one
        card = self.model_cards[mid]
        card.setStyleSheet(card.property('style_selected'))

        self.selected_id = mid
        self.state['model'] = model
        self.state['model']['category'] = category

        task = 'regression'
        if category == 'Classification':
            task = 'classification'
        elif category == 'Clustering':
            task = 'clustering'
        elif category == 'Statistical':
            task = 'time_series'
        self.state['model']['taskType'] = task

        main = self.window()
        if hasattr(main, 'update_sidebar'):
            main.update_sidebar()
            main.statusBar().showMessage(f"✓ Selected: {model['name']}  ({category})")

    def refresh(self):
        # Update recommendation based on data
        types = self.state.get('types', {})
        has_datetime = 'datetime' in types.values()
        if has_datetime:
            self.rec_label.setText("⚡ Datetime column detected → Try ARIMA or SARIMA")
        elif types:
            numeric = sum(1 for v in types.values() if v == 'numeric')
            if numeric > 0:
                self.rec_label.setText("⚡ Numeric data detected → Try XGBoost Regressor or Random Forest")
            else:
                self.rec_label.setText("⚡ Categorical data → Try Classification models")


# ═══════════════════════════════════════════════════════════
# STEP 3 — CONFIGURE FEATURES
# ═══════════════════════════════════════════════════════════
class StepFeatures(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.checkboxes = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(heading_label("// CONFIGURE FEATURES"))
        layout.addWidget(muted_label("Select input features and target variable."))
        layout.addSpacing(4)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {C['border']}; width: 1px; }}")

        # Left: feature checkboxes
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)

        btn_row = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_all.clicked.connect(self.select_all)
        btn_none = QPushButton("Deselect All")
        btn_none.clicked.connect(self.deselect_all)
        btn_row.addWidget(btn_all)
        btn_row.addWidget(btn_none)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        left_layout.addWidget(neon_label("Feature Columns", C['cyan'], 16, True))

        self.features_container = QVBoxLayout()
        self.features_container.setSpacing(4)
        left_layout.addLayout(self.features_container)
        left_layout.addStretch()

        # Right: target + date
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)

        right_layout.addWidget(neon_label("Target Column", C['cyan'], 16, True))
        right_layout.addWidget(muted_label("The variable you want to predict.", 14))
        self.target_combo = QComboBox()
        self.target_combo.currentTextChanged.connect(self._on_target_change)
        right_layout.addWidget(self.target_combo)
        right_layout.addSpacing(16)

        right_layout.addWidget(neon_label("Date Column (optional)", C['cyan'], 16, True))
        right_layout.addWidget(muted_label("For time series models.", 14))
        self.date_combo = QComboBox()
        self.date_combo.addItem("— None —")
        right_layout.addWidget(self.date_combo)
        right_layout.addStretch()

        splitter.addWidget(make_scroll_area(left))
        splitter.addWidget(right)
        splitter.setSizes([500, 300])

        layout.addWidget(splitter, 1)

    def refresh(self):
        # Clear
        while self.features_container.count():
            child = self.features_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.checkboxes.clear()
        self.target_combo.clear()
        self.date_combo.clear()
        self.date_combo.addItem("— None —")

        TYPE_COLORS = {'numeric': C['blue'], 'categorical': C['purple'], 'datetime': C['amber'], 'text': C['muted']}

        for col in self.state.get('columns', []):
            cname = col['name']
            dtype = self.state.get('types', {}).get(cname, 'text')
            tcolor = TYPE_COLORS.get(dtype, C['muted'])

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(8)

            cb = QCheckBox(cname)
            cb.setChecked(True)
            self.checkboxes[cname] = cb
            row_layout.addWidget(cb, 1)
            row_layout.addWidget(badge_label(dtype, tcolor))

            self.features_container.addWidget(row_widget)
            self.target_combo.addItem(cname)

            if dtype == 'datetime':
                self.date_combo.addItem(cname)

        self.state['features'] = {
            'inputs': [c['name'] for c in self.state.get('columns', [])],
            'target': self.target_combo.currentText() if self.target_combo.count() > 0 else '',
            'dateColumn': '',
        }

    def select_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(False)

    def _on_target_change(self, text):
        if text:
            self.state.setdefault('features', {})['target'] = text

    def get_selected_features(self):
        target = self.target_combo.currentText()
        features = [name for name, cb in self.checkboxes.items() if cb.isChecked() and name != target]
        return features, target, self.date_combo.currentText() if self.date_combo.currentIndex() > 0 else None


# ═══════════════════════════════════════════════════════════
# STEP 4 — SET PARAMETERS
# ═══════════════════════════════════════════════════════════
class StepParams(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.param_widgets = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(heading_label("// SET PARAMETERS"))
        self.model_label = muted_label("Tune hyperparameters for your model.")
        layout.addWidget(self.model_label)
        layout.addSpacing(4)

        # Presets row
        preset_row = QHBoxLayout()
        preset_row.addWidget(muted_label("Quick Presets:", 15))
        for name in ['Conservative', 'Balanced', 'Aggressive']:
            btn = QPushButton(name)
            btn.setObjectName('preset')
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(partial(self.apply_preset, name))
            preset_row.addWidget(btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        # Dynamic params area
        self.params_area = QVBoxLayout()
        self.params_area.setSpacing(10)
        layout.addLayout(self.params_area)

        layout.addWidget(separator())

        # Train/test split
        split_group = QGroupBox("Train / Test Split")
        split_layout = QVBoxLayout(split_group)

        split_h = QHBoxLayout()
        self.split_slider = QSlider(Qt.Horizontal)
        self.split_slider.setRange(10, 40)
        self.split_slider.setValue(20)
        self.split_slider.setTickInterval(5)
        self.split_slider.valueChanged.connect(self._update_split_label)
        split_h.addWidget(self.split_slider, 1)
        self.split_label = neon_label("80% Train  /  20% Test", C['cyan'], 15, True)
        split_h.addWidget(self.split_label)
        split_layout.addLayout(split_h)

        self.split_rows_label = muted_label("", 14)
        split_layout.addWidget(self.split_rows_label)
        self._update_split_label(20)

        layout.addWidget(split_group)
        layout.addSpacing(8)

        # Train button
        self.btn_train = QPushButton("⚡  TRAIN MODEL")
        self.btn_train.setObjectName('primary')
        self.btn_train.setFixedHeight(56)
        self.btn_train.setCursor(Qt.PointingHandCursor)
        self.btn_train.clicked.connect(self.start_training)
        layout.addWidget(self.btn_train)

        # Progress
        self.train_progress = QProgressBar()
        self.train_progress.setRange(0, 0)
        self.train_progress.setVisible(False)
        self.train_label = neon_label("Training in progress...", C['cyan'], 15)
        self.train_label.setVisible(False)
        layout.addWidget(self.train_label)
        layout.addWidget(self.train_progress)

        layout.addStretch()

    def _update_split_label(self, val):
        train = 100 - val
        self.split_label.setText(f"{train}% Train  /  {val}% Test")
        rows = self.state.get('shape', {}).get('rows', 0)
        if rows:
            self.split_rows_label.setText(f"Training: {int(rows * train / 100):,} rows  |  Testing: {int(rows * val / 100):,} rows")

    def apply_preset(self, name):
        preset = PRESETS.get(name, {})
        for key, val in preset.items():
            if key in self.param_widgets:
                w = self.param_widgets[key]
                if isinstance(w, QSlider):
                    w.setValue(int(val))
                elif isinstance(w, QSpinBox):
                    w.setValue(int(val))
                elif isinstance(w, QDoubleSpinBox):
                    w.setValue(float(val))

    def refresh(self):
        # Clear old params
        while self.params_area.count():
            child = self.params_area.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        self.param_widgets.clear()

        model = self.state.get('model', {})
        mid = model.get('id', '')
        self.model_label.setText(f"Tune hyperparameters for {model.get('name', 'your model')}.")

        params = DEFAULT_PARAMS.get(mid, {})
        if not params:
            self.params_area.addWidget(muted_label("No hyperparameters for this model. Click Train to proceed.", 16))
            return

        PARAM_TOOLTIPS = {
            'n_estimators': 'Number of trees in the ensemble.',
            'max_depth': 'Maximum depth of each tree.',
            'min_samples_split': 'Minimum samples to split a node.',
            'learning_rate': 'Step size for weight updates.',
            'subsample': 'Fraction of samples for each tree.',
            'colsample_bytree': 'Fraction of features for each tree.',
            'C': 'Regularization. Lower = more regularized.',
            'max_iter': 'Maximum training iterations.',
            'alpha': 'Regularization strength.',
            'n_neighbors': 'Number of nearest neighbors.',
            'n_clusters': 'Number of clusters to create.',
            'eps': 'Max distance between cluster neighbors.',
            'min_samples': 'Min points to form a cluster.',
            'p': 'AR order (past values used).',
            'd': 'Differencing order.',
            'q': 'MA order (past errors used).',
            'P': 'Seasonal AR order.',
            'D': 'Seasonal differencing.',
            'Q': 'Seasonal MA order.',
            'm': 'Seasonal period (e.g. 12 for monthly).',
            'kernel': 'Kernel function for SVM.',
            'units': 'Neurons per hidden layer.',
            'layers': 'Number of hidden layers.',
            'dropout': 'Dropout rate for regularization.',
            'epochs': 'Number of training epochs.',
            'batch_size': 'Samples per training batch.',
        }

        PARAM_RANGES = {
            'n_estimators': (10, 500, 10, 'int'),
            'max_depth': (1, 30, 1, 'int'),
            'min_samples_split': (2, 20, 1, 'int'),
            'learning_rate': (0.001, 0.3, 0.001, 'float'),
            'subsample': (0.5, 1.0, 0.05, 'float'),
            'colsample_bytree': (0.5, 1.0, 0.05, 'float'),
            'C': (0.01, 10.0, 0.01, 'float'),
            'max_iter': (100, 2000, 100, 'int'),
            'alpha': (0.01, 10.0, 0.01, 'float'),
            'n_neighbors': (1, 20, 1, 'int'),
            'n_clusters': (2, 15, 1, 'int'),
            'eps': (0.1, 2.0, 0.1, 'float'),
            'min_samples': (2, 10, 1, 'int'),
            'p': (0, 5, 1, 'int'),
            'd': (0, 2, 1, 'int'),
            'q': (0, 5, 1, 'int'),
            'P': (0, 3, 1, 'int'),
            'D': (0, 2, 1, 'int'),
            'Q': (0, 3, 1, 'int'),
            'm': (1, 52, 1, 'int'),
            'units': (16, 256, 16, 'int'),
            'layers': (1, 4, 1, 'int'),
            'dropout': (0.0, 0.5, 0.05, 'float'),
            'epochs': (10, 200, 10, 'int'),
            'batch_size': (16, 256, 16, 'int'),
        }

        PARAM_OPTIONS = {
            'kernel': ['rbf', 'linear', 'poly', 'sigmoid'],
        }

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)

        row = 0
        for key, default_val in params.items():
            label_text = key.replace('_', ' ').title()
            tooltip = PARAM_TOOLTIPS.get(key, '')

            lbl = QLabel(label_text)
            lbl.setToolTip(tooltip)
            lbl.setStyleSheet(f"color: {C['text']}; font-weight: bold; font-size: 15px;")
            grid.addWidget(lbl, row, 0)

            if key in PARAM_OPTIONS:
                widget = QComboBox()
                for opt in PARAM_OPTIONS[key]:
                    widget.addItem(opt)
                if isinstance(default_val, str):
                    idx = widget.findText(default_val)
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            elif key in PARAM_RANGES:
                mn, mx, step, typ = PARAM_RANGES[key]
                if typ == 'float':
                    widget = QDoubleSpinBox()
                    widget.setRange(mn, mx)
                    widget.setSingleStep(step)
                    widget.setDecimals(3)
                    widget.setValue(float(default_val))
                else:
                    widget = QSpinBox()
                    widget.setRange(int(mn), int(mx))
                    widget.setSingleStep(int(step))
                    widget.setValue(int(default_val))
            else:
                widget = QDoubleSpinBox()
                widget.setRange(0, 99999)
                widget.setValue(float(default_val) if isinstance(default_val, (int, float)) else 0)

            widget.setMinimumWidth(160)
            grid.addWidget(widget, row, 1)

            if tooltip:
                tip = QLabel("?")
                tip.setToolTip(tooltip)
                tip.setStyleSheet(f"""
                    color: {C['muted']}; background: {C['border']};
                    border-radius: 10px; font-size: 10px; font-weight: bold;
                    min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px;
                    qproperty-alignment: AlignCenter;
                """)
                grid.addWidget(tip, row, 2)

            self.param_widgets[key] = widget
            row += 1

        params_w = QWidget()
        params_w.setLayout(grid)
        self.params_area.addWidget(params_w)
        self._update_split_label(self.split_slider.value())

    def get_params(self):
        result = {}
        for key, widget in self.param_widgets.items():
            if isinstance(widget, QComboBox):
                result[key] = widget.currentText()
            elif isinstance(widget, QDoubleSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QSlider):
                result[key] = widget.value()
        return result

    def start_training(self):
        main = self.window()
        features_step = main.step_features
        features, target, date_col = features_step.get_selected_features()

        if not features:
            QMessageBox.warning(self, "No Features", "Select at least one feature column.")
            return
        model = self.state.get('model', {})
        if model.get('taskType') != 'clustering' and not target:
            QMessageBox.warning(self, "No Target", "Select a target column.")
            return

        body = {
            'file_id': self.state.get('file_id'),
            'model_type': model.get('id'),
            'feature_columns': features,
            'target_column': target,
            'params': self.get_params(),
            'test_size': self.split_slider.value() / 100.0,
            'date_column': date_col,
        }

        self.btn_train.setEnabled(False)
        self.train_progress.setVisible(True)
        self.train_label.setVisible(True)

        self.worker = TrainWorker(body)
        self.worker.finished.connect(self.on_train_success)
        self.worker.error.connect(self.on_train_error)
        self.worker.start()

    def on_train_success(self, data):
        self.btn_train.setEnabled(True)
        self.train_progress.setVisible(False)
        self.train_label.setVisible(False)

        model = self.state.get('model', {})
        data['modelName'] = model.get('name', '')
        data['modelId'] = model.get('id', '')
        data['params'] = self.get_params()
        data['timestamp'] = datetime.now().isoformat()
        self.state['results'] = data

        main = self.window()
        if hasattr(main, 'go_to_step'):
            main.step_results.refresh()
            main.go_to_step(4)
            main.update_sidebar()
            main.statusBar().showMessage(f"✓ Training complete — {model.get('name', '')} in {data.get('training_time_seconds', 0):.2f}s")

    def on_train_error(self, msg):
        self.btn_train.setEnabled(True)
        self.train_progress.setVisible(False)
        self.train_label.setVisible(False)
        QMessageBox.critical(self, "Training Error", msg)


# ═══════════════════════════════════════════════════════════
# STEP 5 — RESULTS
# ═══════════════════════════════════════════════════════════
class StepResults(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(16)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(heading_label("// RESULTS"))
        self.results_container = QVBoxLayout()
        self.results_container.setSpacing(12)
        self.layout.addLayout(self.results_container)
        self.layout.addStretch()

    def refresh(self):
        # Clear
        while self.results_container.count():
            child = self.results_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        r = self.state.get('results')
        if not r:
            self.results_container.addWidget(muted_label("No results yet. Train a model first.", 17))
            return

        # Header
        header = QHBoxLayout()
        header.addWidget(neon_label(f"Model: {r.get('modelName', '?')}", C['text'], 16, True))
        header.addStretch()
        header.addWidget(badge_label(f"⏱ {r.get('training_time_seconds', 0):.2f}s", C['cyan']))
        header.addWidget(badge_label(r.get('task_type', '?').upper(), C['blue']))
        self.results_container.addLayout(header)
        self.results_container.addWidget(separator())

        # Metrics
        metrics = r.get('metrics', {})
        task = r.get('task_type', '')

        METRIC_INFO = {
            'r2':              ('R² Score',       True),
            'mae':             ('MAE',            False),
            'mse':             ('MSE',            False),
            'rmse':            ('RMSE',           False),
            'mape':            ('MAPE',           False),
            'accuracy':        ('Accuracy',       True),
            'precision':       ('Precision',      True),
            'recall':          ('Recall',         True),
            'f1':              ('F1 Score',       True),
            'roc_auc':         ('ROC-AUC',        True),
            'silhouette_score':('Silhouette',     True),
            'inertia':         ('Inertia',        False),
        }

        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(10)
        col = 0
        for key, val in metrics.items():
            if val is None:
                continue
            label, higher_better = METRIC_INFO.get(key, (key.upper(), True))

            # Color coding
            if higher_better:
                color = C['green'] if val > 0.8 else C['amber'] if val > 0.5 else C['magenta']
            else:
                color = C['green'] if val < 0.1 else C['amber'] if val < 0.3 else C['magenta']

            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {C['card']};
                    border: 1px solid {color}44;
                    border-top: 3px solid {color};
                    border-radius: 8px;
                    min-width: 160px;
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.setSpacing(6)
            cl.addWidget(muted_label(label, 13))

            val_label = QLabel(f"{val:.4f}" if isinstance(val, float) else str(val))
            val_label.setStyleSheet(f"color: {color}; font-size: 30px; font-weight: bold; font-family: Consolas, monospace;")
            cl.addWidget(val_label)

            row_pos = col // 5
            col_pos = col % 5
            metrics_grid.addWidget(card, row_pos, col_pos)
            col += 1

        mg_widget = QWidget()
        mg_widget.setLayout(metrics_grid)
        self.results_container.addWidget(mg_widget)

        # Charts
        charts_layout = QHBoxLayout()

        if task == 'regression':
            # Actual vs Predicted
            chart1 = CyberChart(5, 3.5)
            ax = chart1.clear_and_style()
            y_test = r.get('y_test', [])
            y_pred = r.get('y_pred', [])
            if y_test and y_pred:
                ax.scatter(y_test, y_pred, color=C['cyan'], alpha=0.7, s=20, edgecolors='none')
                mn, mx = min(min(y_test), min(y_pred)), max(max(y_test), max(y_pred))
                ax.plot([mn, mx], [mn, mx], color=C['magenta'], linewidth=1, linestyle='--', alpha=0.7)
                ax.set_xlabel('Actual')
                ax.set_ylabel('Predicted')
            ax.set_title('Actual vs Predicted')
            chart1.fig.tight_layout()
            chart1.draw()
            charts_layout.addWidget(chart1)

            # Residuals
            chart2 = CyberChart(5, 3.5)
            ax2 = chart2.clear_and_style()
            residuals = r.get('residuals', [])
            if residuals:
                ax2.hist(residuals, bins=20, color=C['blue'], alpha=0.8, edgecolor=C['cyan'])
            ax2.set_title('Residuals Distribution')
            ax2.set_xlabel('Residual')
            ax2.set_ylabel('Count')
            chart2.fig.tight_layout()
            chart2.draw()
            charts_layout.addWidget(chart2)

        elif task == 'classification':
            # Confusion Matrix
            chart1 = CyberChart(4, 3.5)
            ax = chart1.clear_and_style()
            cm = r.get('confusion_matrix', [])
            if cm:
                cm_arr = np.array(cm)
                im = ax.imshow(cm_arr, cmap='RdPu', aspect='auto')
                for i in range(cm_arr.shape[0]):
                    for j in range(cm_arr.shape[1]):
                        ax.text(j, i, str(cm_arr[i, j]), ha='center', va='center', color=C['text'], fontsize=12, fontweight='bold')
                ax.set_xlabel('Predicted')
                ax.set_ylabel('Actual')
            ax.set_title('Confusion Matrix')
            chart1.fig.tight_layout()
            chart1.draw()
            charts_layout.addWidget(chart1)

            # ROC (if binary)
            y_prob = r.get('y_prob')
            y_test = r.get('y_test', [])
            if y_prob and len(np.unique(y_test)) == 2:
                chart2 = CyberChart(4, 3.5)
                ax2 = chart2.clear_and_style()
                from sklearn.metrics import roc_curve
                if isinstance(y_prob[0], list):
                    probs = [p[1] for p in y_prob]
                else:
                    probs = y_prob
                fpr, tpr, _ = roc_curve(y_test, probs)
                ax2.plot(fpr, tpr, color=C['cyan'], linewidth=2)
                ax2.plot([0, 1], [0, 1], color=C['dim'], linestyle='--')
                ax2.fill_between(fpr, tpr, alpha=0.1, color=C['cyan'])
                ax2.set_xlabel('False Positive Rate')
                ax2.set_ylabel('True Positive Rate')
                ax2.set_title(f"ROC Curve (AUC={metrics.get('roc_auc', 0):.3f})")
                chart2.fig.tight_layout()
                chart2.draw()
                charts_layout.addWidget(chart2)

        elif task == 'clustering':
            chart1 = CyberChart(5, 4)
            ax = chart1.clear_and_style()
            pca = r.get('pca_2d', [])
            labels = r.get('labels', [])
            if pca and labels:
                pca_arr = np.array(pca)
                labels_arr = np.array(labels)
                colors_map = [C['cyan'], C['magenta'], C['blue'], C['green'], C['amber'], C['purple']]
                for cluster_id in np.unique(labels_arr):
                    mask = labels_arr == cluster_id
                    c = colors_map[int(cluster_id) % len(colors_map)]
                    ax.scatter(pca_arr[mask, 0], pca_arr[mask, 1], color=c, alpha=0.7, s=30,
                              label=f'Cluster {cluster_id}', edgecolors='none')
                ax.legend(facecolor=C['panel'], edgecolor=C['border'], labelcolor=C['text'], fontsize=9)
            ax.set_title('Clusters (PCA 2D)')
            chart1.fig.tight_layout()
            chart1.draw()
            charts_layout.addWidget(chart1)

        charts_w = QWidget()
        charts_w.setLayout(charts_layout)
        self.results_container.addWidget(charts_w)

        # Feature importance
        fi = r.get('feature_importances', {})
        if fi:
            chart_fi = CyberChart(8, 3)
            ax = chart_fi.clear_and_style()
            sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)
            names = [x[0] for x in sorted_fi]
            vals = [x[1] for x in sorted_fi]
            bars = ax.barh(names[::-1], vals[::-1], color=C['cyan'], alpha=0.8, edgecolor=C['cyan'])
            ax.set_title('Feature Importance')
            ax.set_xlabel('Importance')
            chart_fi.fig.tight_layout()
            chart_fi.draw()
            self.results_container.addWidget(chart_fi)

        # Save button
        btn_row = QHBoxLayout()
        btn_save = QPushButton("💾  Save Results (JSON)")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.save_results)
        btn_row.addWidget(btn_save)
        btn_row.addStretch()
        self.results_container.addLayout(btn_row)

    def save_results(self):
        r = self.state.get('results', {})
        if not r:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Results", f"happymodel_results_{r.get('modelId', 'model')}.json", "JSON (*.json)")
        if path:
            save_data = {k: v for k, v in r.items()}
            # Convert numpy types
            def convert(obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                if isinstance(obj, (np.floating,)):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj

            with open(path, 'w') as f:
                json.dump(save_data, f, indent=2, default=convert)
            QMessageBox.information(self, "Saved", f"Results saved to {path}")


# ═══════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════
class HappyModelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = {
            'file_id': None,
            'filename': '',
            'columns': [],
            'types': {},
            'preview': [],
            'shape': {},
            'stats': {},
            'model': {},
            'features': {'inputs': [], 'target': '', 'dateColumn': ''},
            'results': None,
        }
        self.current_step = 0
        self.init_ui()

        # Animated corner overlay
        self.corners = CyberpunkCorners(self)
        self.corners.setGeometry(0, 0, self.width(), self.height())
        self.corners.raise_()

        self.check_health()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'corners'):
            self.corners.setGeometry(0, 0, self.width(), self.height())

    def init_ui(self):
        self.setWindowTitle("HappyModel — Cyberpunk ML Studio")
        self.setMinimumSize(1200, 800)
        self.resize(1300, 850)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── SIDEBAR ──
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {C['panel']};
                border-right: 1px solid {C['border']};
            }}
        """)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Logo
        logo_widget = QWidget()
        logo_widget.setStyleSheet(f"background: transparent;")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 20, 20, 10)

        logo = QLabel("HAPPY\nMODEL")
        logo.setStyleSheet(f"""
            color: {C['cyan']};
            font-size: 28px;
            font-weight: bold;
            font-family: Consolas, monospace;
            letter-spacing: 3px;
            line-height: 1.2;
            background: transparent;
        """)
        logo_layout.addWidget(logo)

        tagline = QLabel("CYBERPUNK ML STUDIO")
        tagline.setStyleSheet(f"color: {C['dim']}; font-size: 9px; letter-spacing: 2px; background: transparent;")
        logo_layout.addWidget(tagline)
        sb_layout.addWidget(logo_widget)

        sb_layout.addWidget(separator())
        sb_layout.addSpacing(8)

        # Step buttons
        self.step_names = [
            "01  IMPORT DATA",
            "02  SELECT MODEL",
            "03  FEATURES",
            "04  PARAMETERS",
            "05  RESULTS",
        ]
        self.step_buttons = []
        for i, name in enumerate(self.step_names):
            btn = QPushButton(name)
            btn.setObjectName('step_active' if i == 0 else 'step_btn')
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(partial(self.go_to_step, i))
            sb_layout.addWidget(btn)
            self.step_buttons.append(btn)

        sb_layout.addStretch()

        # Health indicator
        self.health_label = QLabel("  ● BACKEND: CHECKING...")
        self.health_label.setStyleSheet(f"color: {C['amber']}; font-size: 10px; padding: 12px; background: transparent;")
        sb_layout.addWidget(self.health_label)

        main_layout.addWidget(sidebar)

        # ── MAIN CONTENT ──
        content_area = QWidget()
        content_area.setStyleSheet(f"background: {C['bg']};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(28, 24, 28, 16)

        self.stack = QStackedWidget()

        # Create steps
        self.step_import = StepImport(self.state)
        self.step_model = StepModel(self.state)
        self.step_features = StepFeatures(self.state)
        self.step_params = StepParams(self.state)
        self.step_results = StepResults(self.state)

        self.steps = [self.step_import, self.step_model, self.step_features, self.step_params, self.step_results]

        for step in self.steps:
            scroll = make_scroll_area(step)
            self.stack.addWidget(scroll)

        content_layout.addWidget(self.stack, 1)

        # Bottom nav
        bottom = QHBoxLayout()
        self.btn_back = QPushButton("← BACK")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.setFixedHeight(48)
        self.btn_back.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                color: #e0e0ff;
                padding: 0 28px;
            }}
        """)
        self.btn_next = QPushButton("NEXT →")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_next.setFixedHeight(48)
        self.btn_next.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                color: #e0e0ff;
                padding: 0 28px;
            }}
        """)

        bottom.addWidget(self.btn_back)
        bottom.addStretch()
        step_indicator = neon_label("Step 1 of 5", C['muted'], 15)
        self.step_indicator = step_indicator
        bottom.addWidget(step_indicator)
        bottom.addStretch()
        bottom.addWidget(self.btn_next)
        content_layout.addLayout(bottom)

        main_layout.addWidget(content_area, 1)

        # Status bar
        self.statusBar().showMessage("Ready. Upload a file to get started.")
        self.update_nav()

    def check_health(self):
        try:
            resp = requests.get(f'{API_BASE}/health', timeout=3)
            if resp.status_code == 200:
                self.health_label.setText("  ● BACKEND: ONLINE")
                self.health_label.setStyleSheet(f"color: {C['green']}; font-size: 10px; padding: 12px; background: transparent;")
            else:
                raise Exception()
        except:
            self.health_label.setText("  ● BACKEND: OFFLINE")
            self.health_label.setStyleSheet(f"color: {C['magenta']}; font-size: 10px; padding: 12px; background: transparent;")

    def go_to_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
        self.current_step = idx
        self.stack.setCurrentIndex(idx)

        # Refresh step data
        if idx == 1:
            self.step_model.refresh()
        elif idx == 2:
            self.step_features.refresh()
        elif idx == 3:
            self.step_params.refresh()
        elif idx == 4:
            self.step_results.refresh()

        self.update_sidebar()
        self.update_nav()

    def go_back(self):
        if self.current_step > 0:
            self.go_to_step(self.current_step - 1)

    def go_next(self):
        if self.current_step < len(self.steps) - 1:
            self.go_to_step(self.current_step + 1)

    def update_sidebar(self):
        for i, btn in enumerate(self.step_buttons):
            if i == self.current_step:
                btn.setObjectName('step_active')
            else:
                btn.setObjectName('step_btn')
            btn.setStyle(btn.style())  # force restyle

    def update_nav(self):
        self.btn_back.setEnabled(self.current_step > 0)
        self.btn_next.setEnabled(self.current_step < len(self.steps) - 1)
        self.step_indicator.setText(f"Step {self.current_step + 1} of 5")


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(C['bg']))
    palette.setColor(QPalette.WindowText, QColor(C['text']))
    palette.setColor(QPalette.Base, QColor(C['input_bg']))
    palette.setColor(QPalette.AlternateBase, QColor(C['card']))
    palette.setColor(QPalette.ToolTipBase, QColor(C['card']))
    palette.setColor(QPalette.ToolTipText, QColor(C['text']))
    palette.setColor(QPalette.Text, QColor(C['text']))
    palette.setColor(QPalette.Button, QColor(C['panel']))
    palette.setColor(QPalette.ButtonText, QColor(C['text']))
    palette.setColor(QPalette.BrightText, QColor(C['cyan']))
    palette.setColor(QPalette.Highlight, QColor(C['cyan']))
    palette.setColor(QPalette.HighlightedText, QColor(C['bg']))
    app.setPalette(palette)

    window = HappyModelApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
