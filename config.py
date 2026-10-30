import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Check if running in serverless environment (Vercel, AWS Lambda)
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

# Database path: use /tmp on serverless environments because /var/task is read-only
if IS_SERVERLESS:
    DATABASE_PATH = Path("/tmp") / "landslide.db"
else:
    DATABASE_PATH = BASE_DIR / "data" / "landslide.db"

# ML model
MODEL_PATH = BASE_DIR / "models" / "landslide_model.pkl"

# Flask
HOST = "127.0.0.1"
PORT = int(os.getenv("PORT", 5000))
DEBUG = not IS_SERVERLESS

# Application
APP_NAME = "Localized Landslide Risk Monitoring System"

# Risk thresholds - prototype values
SHI_LOW = 30
SHI_MODERATE = 55
SHI_HIGH = 75

# API
API_PREFIX = "/api"
