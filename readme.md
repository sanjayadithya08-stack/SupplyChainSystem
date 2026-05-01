<div align="center">
  <h1>🚢 AI-Powered Supply Chain Disruption Predictor & Preventer</h1>
  <p><i>A fault-tolerant, production-ready system utilizing the <b>Antigravity Architecture</b> to predict and actively prevent global supply chain disruptions.</i></p>
  
  ![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
  ![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)
</div>

---

## 🌟 Overview

Supply chains are vulnerable to countless unpredictable events—from port strikes and extreme weather to cyberattacks and geopolitical conflicts. 

This project is a **Predictive & Preventive AI System**. It doesn't just warn you about a problem; it generates an immediate action plan. Powered by a Random Forest NLP model, it reads unstructured live intelligence (News, Weather, Geo-events), predicts the compounding risk, and triggers automated action plans to reroute logistics and switch suppliers before the disruption hits.

### Core Features
- **🤖 Intelligence Engine**: Parses unstructured text to predict *Risk Level* and *Disruption Type*.
- **🛡️ Prevention Engine**: Dynamically generates Immediate, Short-term, and Long-term mitigation checklists.
- **🗺️ Interactive Map**: Real-time supplier tier tracking and shipping route delay estimations.
- **⚡ Antigravity Architecture**: Designed with strict fault tolerance. If an external API or model fails, the system automatically degrades gracefully instead of crashing.
- **📊 6-Tab Command Center**: A premium Streamlit dashboard for manual analysis, batch processing, and live global radar monitoring.

---

## 📂 Project Structure

```text
C:\SupplyChain\
├── api/
│   ├── main.py                   <- FastAPI Endpoints
│   ├── middleware.py             <- Fault-tolerance tracking
│   └── schemas.py                <- Pydantic Models
├── data/
│   ├── dataset.csv               <- Training data (60+ Scenarios)
│   └── augment_data.py           <- Automated data multiplier
├── ml/
│   ├── prevention_engine.py      <- Brain that maps risk to actions
│   ├── train_model.py            <- TF-IDF & Random Forest pipeline
│   └── predict.py                <- Inference logic
├── services/
│   ├── alert_service.py          <- Automated email/log alerts
│   ├── supplier_service.py       <- Supplier tiers & risk scoring
│   ├── route_service.py          <- Transit routes & delay tracking
│   ├── news_service.py           <- Live Global Headlines API Stub
│   ├── weather_service.py        <- Weather API Stub
│   └── geo_service.py            <- Geopolitical API Stub
├── ui/
│   ├── app.py                    <- Streamlit 6-Tab Interface
│   └── components.py             <- Premium CSS and rendering functions
├── utils/
│   ├── config.py                 <- Master Configuration
│   └── text_preprocessing.py     <- NLP cleaning
├── logs/                         <- Alert & Prediction audit trails
└── run.py                        <- Master Application Launcher
```

---

## 🚀 Quick Start Guide

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file:
```bash
# On Windows:
Copy-Item .env.example -Destination .env
# On Mac/Linux:
cp .env.example .env
```

### 3. Train the AI Model
Initialize the dataset and train the Random Forest classifier:
```bash
python run.py train
```
*Note: This will auto-generate the TF-IDF vectorizer and model pipeline into `ml/artefacts/`.*

### 4. Launch the System
Start the FastAPI backend and Streamlit dashboard simultaneously:
```bash
python run.py all
```
The **Command Center Dashboard** will automatically open in your browser at `http://localhost:8501`.

---

## 🏗️ The Antigravity Architecture

This application was strictly designed around the **Antigravity Principle**: *No single point of failure should collapse the system.*

1. **Graceful Degradation:** If the ML model file is accidentally deleted, the system stays online and returns `UNKNOWN` risk rather than throwing a 500 server error.
2. **Resilient UI:** If the backend API goes offline, the Streamlit dashboard detects the outage, displays a warning banner, and keeps the UI active.
3. **In-Memory Caching:** External API calls (like fetching live news or weather) are protected by caching services to prevent rate-limiting and guarantee rapid dashboard reloads.