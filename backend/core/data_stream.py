import random
from datetime import datetime, timezone

ANOMALY_TRIGGERS = [
    "Water quality drop detected",
    "Pharmacy purchase spike",
    "Reported case cluster",
    "Sanitation failure logged",
]

def generate_proxy_signal(districts: list) -> dict:
    """Simulates an incoming environmental anomaly signal."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "district": random.choice(districts),
        "risk_score": round(random.uniform(0.6, 0.99), 2),
        "trigger": random.choice(ANOMALY_TRIGGERS),
    }

def generate_normal_signal(districts: list) -> dict:
    """Simulates normal/stable conditions."""
    return {
       "timestamp": datetime.now(timezone.utc).isoformat(),
        "district": random.choice(districts),
        "risk_score": round(random.uniform(0.05, 0.2), 2),
        "trigger": "Normal conditions",
    }

if __name__ == "__main__":
    districts = ["Hub_A", "Clinic_B", "District_C", "Village_D", "Outpost_E"]
    print(generate_proxy_signal(districts))