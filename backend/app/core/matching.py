from __future__ import annotations

from datetime import datetime, time, timedelta
from math import radians, sin, cos, asin, sqrt
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from ..models.models import Nonprofit, PickupWindow, Donation


def parse_hhmm(value: str) -> time:
    hour_str, minute_str = value.split(":", 1)
    hour = int(hour_str)
    minute = int(minute_str)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Invalid HH:MM time")
    return time(hour=hour, minute=minute)


def window_overlaps(donation_start: time, donation_end: time, win_start: time, win_end: time) -> bool:
    # Normalize potential wrap-around windows by mapping to minutes since midnight and duplicating range
    def to_minutes(t: time) -> int:
        return t.hour * 60 + t.minute

    ds, de = to_minutes(donation_start), to_minutes(donation_end)
    ws, we = to_minutes(win_start), to_minutes(win_end)

    def intervals(start: int, end: int):
        if start <= end:
            return [(start, end)]
        # wraps midnight
        return [(start, 24 * 60), (0, end)]

    d_intervals = intervals(ds, de)
    w_intervals = intervals(ws, we)

    for d1, d2 in d_intervals:
        for w1, w2 in w_intervals:
            if max(d1, w1) < min(d2, w2):
                return True
    return False


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in kilometers
    r = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def compute_pickup_eta(donation_ready_at: datetime, win_start: time, win_end: time) -> Optional[datetime]:
    date = donation_ready_at.date()
    start_dt = datetime.combine(date, win_start)
    end_dt = datetime.combine(date, win_end)

    # handle wrap-around windows by allowing end on next day
    if end_dt <= start_dt:
        end_dt = end_dt + timedelta(days=1)
        if donation_ready_at.time() < win_start:
            # same-day before window start
            pass
        else:
            # donation is later in the day; if after end next day might be valid
            pass
    candidate = max(donation_ready_at, start_dt)
    if candidate <= end_dt:
        return candidate
    return None


def find_best_nonprofit(db: Session, donation: Donation) -> Optional[Tuple[Nonprofit, float, datetime]]:
    donation_start_t = donation.ready_at.time()
    donation_end_t = donation.expires_at.time()

    nonprofits: list[Nonprofit] = (
        db.query(Nonprofit).filter(Nonprofit.active == True).all()  # noqa: E712
    )

    best: Optional[Tuple[Nonprofit, float, datetime]] = None

    for np in nonprofits:
        if not np.pickup_windows:
            continue
        for win in np.pickup_windows:
            try:
                ws = parse_hhmm(win.start_time)
                we = parse_hhmm(win.end_time)
            except Exception:
                continue
            if not window_overlaps(donation_start_t, donation_end_t, ws, we):
                continue
            eta = compute_pickup_eta(donation.ready_at, ws, we)
            if eta is None or eta > donation.expires_at:
                continue
            distance = haversine_km(donation.latitude, donation.longitude, np.latitude, np.longitude)
            if best is None or distance < best[1]:
                best = (np, distance, eta)
    return best
