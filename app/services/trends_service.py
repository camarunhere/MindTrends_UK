"""
Retrieve Google Trends Data
============================
Central service backing the "Retrieve Google Trends Data" use case.

Because Google Trends has no official, guaranteed-stable public API for every
use case, this service wraps the unofficial `pytrends` client and transparently
falls back to a deterministic, clearly-labelled *simulated* series whenever:
  - the admin has forced simulated mode,
  - pytrends is unavailable / not installed,
  - Google Trends rate-limits or errors on the request.

Every response carries a `source` field ("live" | "simulated" | "cache") and a
`warnings` list so the UI (and the dissertation write-up) can be fully
transparent about how the data was obtained - this mirrors the guidance in
the project brief.
"""

import hashlib
import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from app.extensions import db
from app.models.settings import Settings

try:
    from pytrends.request import TrendReq

    PYTRENDS_AVAILABLE = True
except Exception:  # pragma: no cover - import guard
    PYTRENDS_AVAILABLE = False


def _cache_key(term, geo, timeframe, category):
    raw = f"{term}|{geo}|{timeframe}|{category}".lower()
    return hashlib.sha256(raw.encode()).hexdigest()


def _resolve_timeframe(timeframe_value):
    return timeframe_value.replace("{today}", datetime.utcnow().strftime("%Y-%m-%d"))


def _from_cache(cache_key, ttl_minutes):
    doc = db.trend_cache.find_one({"cache_key": cache_key})
    if not doc:
        return None
    age = datetime.now(timezone.utc) - doc["fetched_at"].replace(tzinfo=timezone.utc)
    if age > timedelta(minutes=ttl_minutes):
        return None
    payload = dict(doc["payload"])
    payload["source"] = "cache"
    payload["warnings"] = doc["payload"].get("warnings", [])
    return payload


def _store_cache(cache_key, payload):
    db.trend_cache.update_one(
        {"cache_key": cache_key},
        {
            "$set": {
                "cache_key": cache_key,
                "payload": payload,
                "fetched_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )


def _simulate_series(term, geo, timeframe, category):
    """Deterministic synthetic series: same inputs => same output.

    Built from a seeded RNG so demo runs are reproducible, with a slow trend
    component, an annual seasonal component and bounded noise, clipped to the
    0-100 scale Google Trends itself uses for relative search interest.
    """
    seed = int(_cache_key(term, geo, timeframe, category)[:8], 16)
    rng = np.random.default_rng(seed)

    n_points = 60
    end = datetime.utcnow().replace(day=1)
    dates = pd.date_range(end=end, periods=n_points, freq="MS")

    base = 30 + (seed % 25)
    trend = np.linspace(0, rng.uniform(-10, 25), n_points)
    seasonal = 8 * np.sin(np.linspace(0, 6 * math.pi, n_points) + seed % 6)
    noise = rng.normal(0, 5, n_points)
    series = base + trend + seasonal + noise
    series = np.clip(series, 0, 100)
    # Rescale so the peak hits close to 100, echoing real Google Trends scaling
    series = series * (100 / max(series.max(), 1))
    series = np.round(series).astype(int)

    return {
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "values": series.tolist(),
        "source": "simulated",
        "sparse": False,
        "warnings": [
            "Simulated data: live Google Trends data was not used for this "
            "series. Values are synthetically generated for demonstration "
            "purposes only and do not reflect real search interest."
        ],
    }


def _fetch_live(term, geo, timeframe, category, request_timeout):
    pytrends = TrendReq(hl="en-GB", tz=0, timeout=(request_timeout, request_timeout))
    kw_list = [term]
    pytrends.build_payload(
        kw_list, cat=category or 0, timeframe=timeframe, geo=geo or "GB"
    )
    df = pytrends.interest_over_time()
    if df is None or df.empty:
        raise ValueError("Google Trends returned no data for this query.")
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])
    series = df[term]
    return series


def retrieve_trends(term, geo, timeframe_value, category=0, force_refresh=False):
    """Main entry point for the 'Retrieve Google Trends Data' use case.

    Includes «Set Parameters» (term/geo/timeframe/category are required
    inputs) and extends into «Filter Data», «Normalize & Process Data» and
    «Handle Missing / Sparse Data» as described by the use-case diagram.
    """
    settings = Settings.get_retrieval_settings()
    mode = settings["mode"]
    timeframe = _resolve_timeframe(timeframe_value)
    cache_key = _cache_key(term, geo, timeframe, category)

    if not force_refresh:
        cached = _from_cache(cache_key, settings["cache_ttl_minutes"])
        if cached:
            return cached

    payload = None
    if mode != "simulated" and PYTRENDS_AVAILABLE:
        try:
            series = _fetch_live(term, geo, timeframe, category, settings["request_timeout"])
            values = series.fillna(0).tolist()
            dates = [d.strftime("%Y-%m-%d") for d in series.index]
            non_zero_ratio = (sum(1 for v in values if v > 0) / len(values)) if values else 0
            sparse = non_zero_ratio < 0.25
            warnings = []
            if sparse:
                warnings.append(
                    "Data appears sparse: fewer than 25% of data points have "
                    "non-zero search interest for this term/region/time "
                    "combination. Interpret trends with caution."
                )
            payload = {
                "dates": dates,
                "values": [int(v) for v in values],
                "source": "live",
                "sparse": sparse,
                "warnings": warnings,
            }
        except Exception as exc:  # noqa: BLE001 - broad by design, network/library errors vary
            if mode == "live":
                payload = {
                    "dates": [],
                    "values": [],
                    "source": "error",
                    "sparse": True,
                    "warnings": [f"Live retrieval failed and simulated mode is disabled: {exc}"],
                }
            # else fall through to simulated below

    if payload is None:
        payload = _simulate_series(term, geo, timeframe, category)

    payload = normalize_series(payload)
    _store_cache(cache_key, payload)
    return payload


def normalize_series(payload):
    """Normalize & Process Data: ensures a clean, continuous, sorted series."""
    if not payload.get("dates"):
        return payload
    df = pd.DataFrame({"date": pd.to_datetime(payload["dates"]), "value": payload["values"]})
    df = df.sort_values("date").drop_duplicates(subset="date")
    df["value"] = df["value"].clip(lower=0, upper=100)
    payload["dates"] = df["date"].dt.strftime("%Y-%m-%d").tolist()
    payload["values"] = df["value"].astype(int).tolist()
    return payload
