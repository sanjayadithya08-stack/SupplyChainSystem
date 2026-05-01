from dataclasses import dataclass
from datetime import datetime
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

@dataclass
class Alert:
    id: str
    level: str # INFO, WARNING, CRITICAL, EMERGENCY
    message: str
    recipients: list[str]
    timestamp: str
    acknowledged: bool

def send_alert(level: str, message: str, recipients: list[str]) -> bool:
    """
    Stub that logs alert to logs/alerts.log
    
    # TO SWAP FOR REAL EMAIL (e.g. SMTP/SendGrid):
    # import smtplib
    # server = smtplib.SMTP('smtp.sendgrid.net', 587)
    # server.login('apikey', os.getenv('SENDGRID_API_KEY'))
    # server.sendmail("system@supplychain.com", recipients, f"Subject: {level} Alert\n\n{message}")
    """
    try:
        alert = Alert(
            id=f"ALT-{int(datetime.utcnow().timestamp())}",
            level=level,
            message=message,
            recipients=recipients,
            timestamp=datetime.utcnow().isoformat(),
            acknowledged=False
        )
        
        with open(Config.ALERTS_LOG_PATH, "a") as f:
            f.write(json.dumps(alert.__dict__) + "\n")
            
        print(f"[{level}] Alert Sent to {recipients}: {message[:50]}...")
        return True
    except Exception as e:
        print(f"Error sending alert: {e}")
        return False

def send_prevention_plan(plan: dict, recipients: list[str]) -> bool:
    try:
        priority = plan.get("priority", "P3")
        level = "EMERGENCY" if priority == "P1" else "WARNING" if priority == "P2" else "INFO"
        
        message = "Supply Chain Action Required:\n\nImmediate Actions:\n"
        for act in plan.get("immediate_actions", []):
            message += f"- {act}\n"
            
        return send_alert(level, message, recipients)
    except Exception as e:
        print(f"Error sending prevention plan: {e}")
        return False

def get_recent_alerts(n: int = 10) -> list[Alert]:
    try:
        if not os.path.exists(Config.ALERTS_LOG_PATH):
            return []
            
        alerts = []
        with open(Config.ALERTS_LOG_PATH, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if not line.strip(): continue
                data = json.loads(line)
                alerts.append(Alert(**data))
                if len(alerts) >= n: break
        return alerts
    except Exception as e:
        print(f"Error getting alerts: {e}")
        return []
