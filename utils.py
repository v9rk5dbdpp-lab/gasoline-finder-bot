import math
from datetime import datetime, timedelta
from typing import Optional, Dict


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расчёт расстояния между двумя точками на Земле в километрах"""
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_suspicious_report(
    last_report: Optional[dict],
    new_lat: Optional[float],
    new_lon: Optional[float],
    min_time_minutes: int = 5,
    max_distance_km: int = 80
) -> bool:
    """Проверяет, подозрительный ли отчёт (быстро + далеко)"""
    if not last_report or not last_report.get("latitude") or not last_report.get("longitude"):
        return False
    if not new_lat or not new_lon:
        return False

    try:
        last_time = datetime.fromisoformat(last_report.get("created_at", "").replace("Z", "+00:00"))
    except:
        return False

    time_diff = datetime.now() - last_time.replace(tzinfo=None)
    if time_diff.total_seconds() / 60 > min_time_minutes:
        return False

    distance = haversine_distance(
        last_report["latitude"], last_report["longitude"],
        new_lat, new_lon
    )
    return distance > max_distance_km