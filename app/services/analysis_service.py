"""
Trend Analysis / Insights + Compare Disorders / Regions
=========================================================
Turns a raw (already normalized) trend series into research-oriented
insights: direction, peaks, percentage change, and a plain-language summary
that is careful never to claim anything about real-world prevalence -
only about *search interest*.
"""

import pandas as pd


def analyse_series(label, dates, values):
    if not values:
        return {
            "label": label,
            "average": 0,
            "peak_value": 0,
            "peak_date": None,
            "start_value": 0,
            "end_value": 0,
            "change_pct": 0,
            "direction": "flat",
            "insight": f"No usable search-interest data was available for {label}.",
        }

    series = pd.Series(values, index=pd.to_datetime(dates))
    peak_idx = series.idxmax()
    start_value = int(series.iloc[0])
    end_value = int(series.iloc[-1])
    change_pct = (
        round(((end_value - start_value) / start_value) * 100, 1)
        if start_value > 0
        else 0
    )

    if change_pct > 10:
        direction = "increasing"
    elif change_pct < -10:
        direction = "decreasing"
    else:
        direction = "stable"

    insight = (
        f"Search interest for '{label}' was {direction} over the selected "
        f"period, moving from {start_value} to {end_value} "
        f"({'+' if change_pct >= 0 else ''}{change_pct}%), with a peak "
        f"relative interest of {int(series.max())} around "
        f"{peak_idx.strftime('%B %Y')}."
    )

    return {
        "label": label,
        "average": round(float(series.mean()), 1),
        "peak_value": int(series.max()),
        "peak_date": peak_idx.strftime("%Y-%m-%d"),
        "start_value": start_value,
        "end_value": end_value,
        "change_pct": change_pct,
        "direction": direction,
        "insight": insight,
    }


def compare_series(series_list):
    """series_list: list of {label, dates, values} -> comparison summary."""
    analyses = [analyse_series(s["label"], s["dates"], s["values"]) for s in series_list]
    if not analyses:
        return {"analyses": [], "leader": None, "summary": ""}

    leader = max(analyses, key=lambda a: a["average"])
    fastest_rising = max(analyses, key=lambda a: a["change_pct"])

    summary = (
        f"Across the compared series, '{leader['label']}' recorded the "
        f"highest average relative search interest ({leader['average']}). "
        f"'{fastest_rising['label']}' showed the largest increase over the "
        f"period ({'+' if fastest_rising['change_pct'] >= 0 else ''}"
        f"{fastest_rising['change_pct']}%)."
    )

    return {"analyses": analyses, "leader": leader["label"], "summary": summary}
