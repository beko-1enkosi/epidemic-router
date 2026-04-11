import random
from datetime import datetime, timezone

ANOMALY_TRIGGERS = [
    "Water quality drop detected",
    "Pharmacy purchase spike",
    "Reported case cluster",
    "Sanitation failure logged",
]


def _build_signal(districts: list[str], min_risk: float, max_risk: float, trigger: str | None = None) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "district": random.choice(districts),
        "risk_score": round(random.uniform(min_risk, max_risk), 2),
        "trigger": trigger or random.choice(ANOMALY_TRIGGERS),
    }


def generate_proxy_signal(districts: list[str]) -> dict:
    """Simulates an incoming environmental anomaly signal."""
    return _build_signal(districts, 0.6, 0.99)


def generate_normal_signal(districts: list[str]) -> dict:
    """Simulates stable environmental conditions."""
    return _build_signal(districts, 0.05, 0.2, "Normal conditions")


if __name__ == "__main__":
    districts = ["Hub_A", "Clinic_B", "District_C", "Village_D", "Outpost_E"]
    print(generate_proxy_signal(districts))