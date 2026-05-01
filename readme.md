<div align="center">
  <h1>🚢 TechCore: Enterprise Supply Chain Intelligence</h1>
  <p><i>A production-grade, autonomous platform for tracking active shipments, predicting disruptions, and executing automated mitigation plans.</i></p>
  
  ![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
  ![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)
  ![SQLite](https://img.shields.io/badge/SQLite-3.0+-blue.svg)
</div>

---

## 🌟 Overview

**TechCore SupplyChain AI** is a shipment-centric intelligence platform designed to move logistics from reactive to proactive. Unlike generic news trackers, this system centers strictly on your company's operational data—tracking every active shipment, correlating global events (weather, strikes, geopolitical) to specific transit routes, and autonomously notifying stakeholders when revenue is at risk.

---

## 🚀 Key Features

- **📦 Live Shipment Ledger**: Real-time tracking of active cargo, SKU-level value in transit, and dynamic ETA monitoring.
- **📡 AI Threat Radar**: An automated engine that cross-references live news, weather, and geo-signals against active shipment routes to predict disruptions using a Gradient Boosting ML model.
- **📧 Autonomous Mitigation**: Automatically dispatches prevention plans and risk alerts to the **Sender (Supplier)** and **Receiver** via Email/Slack when critical threats are detected.
- **📰 Live Intelligence Feed**: A curated, real-time disruption feed with direct links to original sources and AI-assigned severity levels.
- **🩺 System Monitor**: Real-time health dashboard tracking API status, model load state, and server resource utilization (CPU, RAM, Disk).
- **📈 Company Analytics**: Historical analysis of supplier reliability, revenue-at-risk trends, and disruption frequency.

---

## 📂 Project Structure

```text
C:\SupplyChain\
├── api/
│   ├── main.py                   <- FastAPI Endpoints (Shipments, Threats, News)
│   ├── schemas.py                <- Pydantic Models for system communication
├── db/
│   ├── models.py                 <- SQLAlchemy Models (Shipments, Suppliers, Routes)
├── data/
│   └── supplychain.db            <- SQLite Production Database
├── ml/
│   ├── live_threat_engine.py     <- Core Correlation Engine (Threats + Shipments)
│   ├── company_predict.py        <- ML Inference (Gradient Boosting)
│   ├── prevention_engine.py      <- Action plan generator
│   └── train_model.py            <- Training pipeline for TechCore data
├── services/
│   ├── shipment_service.py       <- Active shipment management
│   ├── alert_service.py          <- Automated dispatch (Email/Slack/Log)
│   ├── news_service.py           <- Live Global Intelligence API
│   ├── weather_service.py        <- Real-time Weather monitoring
│   └── geo_service.py            <- Geopolitical event tracking
├── ui/
│   ├── app.py                    <- Premium 6-Tab Command Center
│   └── components.py             <- Modern CSS & UI Component Library
├── utils/
│   └── config.py                 <- Master Configuration & Environment
└── logs/                         <- Automated Alert & Audit Trails
```

---

## 🛠️ Setup & Execution

### 1. Installation
```bash
# Activate your environment and install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Ensure your `.env` file contains the necessary keys for full functionality:
- `NEWS_API_KEY`: For live intelligence feed.
- `GEMINI_API_KEY`: For AI-generated executive summaries.
- `SLACK_WEBHOOK_URL`: For automated team notifications.

### 3. Launching the Platform
Start both the backend intelligence engine and the frontend command center:
```bash
python run.py all
```
Access the dashboard at `http://localhost:8501`.

---

## 🧠 Intelligence Workflow

1. **Ingest**: The system monitors the internal SQLite database for all shipments marked "In Transit".
2. **Scan**: It polls live global APIs for news, weather, and geopolitical events.
3. **Correlate**: The **Live Threat Engine** identifies overlaps between external events and active shipment regions/routes.
4. **Predict**: The Gradient Boosting model calculates the probability of delay and total revenue at risk.
5. **Mitigate**: If risk is HIGH/CRITICAL, the system autonomously emails the specific Supplier and Receiver with an immediate action plan.