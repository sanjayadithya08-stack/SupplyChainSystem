import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    # API Settings
    API_PORT = int(os.getenv("API_PORT", 8000))
    UI_PORT = int(os.getenv("UI_PORT", 8501))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")

    # Paths
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    ML_DIR = os.path.join(PROJECT_ROOT, "ml")
    ARTEFACTS_DIR = os.path.join(ML_DIR, "artefacts")
    LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
    
    DATASET_PATH = os.path.join(DATA_DIR, "dataset.csv")
    AUGMENTED_DATASET_PATH = os.path.join(DATA_DIR, "augmented_dataset.csv")
    MODEL_PATH = os.path.join(ARTEFACTS_DIR, "model.pkl")
    PIPELINE_PATH = os.path.join(ARTEFACTS_DIR, "pipeline.pkl")
    TRAINING_REPORT_PATH = os.path.join(ARTEFACTS_DIR, "training_report.json")
    
    PREDICTIONS_LOG_PATH = os.path.join(LOGS_DIR, "predictions.log")
    ALERTS_LOG_PATH = os.path.join(LOGS_DIR, "alerts.log")

    # Constants & Thresholds
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL", 300))
    RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    DEFAULT_RISK = "UNKNOWN"
    
    # Alert Recipients
    ALERT_EMAIL = os.getenv("ALERT_EMAIL", "ops@yourcompany.com")
    ALERT_RECIPIENTS = [ALERT_EMAIL, "supplychain-exec@yourcompany.com", "it-sec@yourcompany.com"]
    
    # Master Lists
    REGIONS = [
        "global", "us-west-coast", "us-east-coast", "north-america", 
        "latin-america", "europe", "middle-east", "south-asia", 
        "southeast-asia", "east-asia", "oceania"
    ]
    
    DISRUPTION_TYPES = [
        "port_strike", "weather", "war", "cyber", 
        "logistics", "supplier", "customs", "normal"
    ]

# Ensure directories exist
os.makedirs(Config.DATA_DIR, exist_ok=True)
os.makedirs(Config.ARTEFACTS_DIR, exist_ok=True)
os.makedirs(Config.LOGS_DIR, exist_ok=True)
