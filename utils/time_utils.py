import random
from datetime import datetime, timezone, timedelta

def rfc1123_gmt(dt: datetime) -> str:
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

def random_time_today_gmt() -> str:
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    random_seconds = random.randint(0, 86399)
    return rfc1123_gmt(start_of_day + timedelta(seconds=random_seconds))