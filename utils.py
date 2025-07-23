from datetime import datetime, timedelta
import hashlib

def now():
    return datetime.utcnow().isoformat()

def today():
    return datetime.utcnow().date().isoformat()

def get_next_cycle_time():
    now_dt = datetime.utcnow()
    hours = (now_dt.hour // 4 + 1) * 4
    next_cycle = now_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=hours)
    if next_cycle <= now_dt:
        next_cycle += timedelta(hours=4)
    return next_cycle.isoformat()

def get_ip_hash(ip: str):
    return hashlib.sha256(ip.encode()).hexdigest()
