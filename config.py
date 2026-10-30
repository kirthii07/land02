import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = BASE_DIR / "data" / "landslide.db"

# ML model
MODEL_PATH = BASE_DIR / "models" / "landslide_model.pkl"

# Flask
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# Application
APP_NAME = "Localized Landslide Risk Monitoring System"

# Risk thresholds - prototype values
SHI_LOW = 30
SHI_MODERATE = 55
SHI_HIGH = 75

# API
API_PREFIX = "/api"