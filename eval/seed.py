# agentlens/eval/seed.py
import sys
sys.path.insert(0, r"C:\Users\MSI\Desktop\ahmedaskri\Sentinel")

from incident_db import log_incident

def seed_history(camera_id, event_type, decisions, base_timestamp="2026-01-01T00:00:00"):
    """Insert fake past incidents so query_past_incidents finds them."""
    for decision in decisions:
        log_incident(camera_id, event_type, 0.80, base_timestamp, decision)