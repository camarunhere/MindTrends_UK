"""Orchestrates a full researcher query: select disorder(s) + parameters ->
retrieve -> normalize -> analyse -> compare. Shared by the dashboard page
(initial render) and the AJAX refine endpoint under /api.
"""

from app.models.disorder import Disorder
from app.services.analysis_service import compare_series
from app.services.trends_service import retrieve_trends


def run_query(disorder_ids, region_codes, timeframe_value, category=0):
    disorders = [Disorder.get_by_id(did) for did in disorder_ids]
    disorders = [d for d in disorders if d]
    if not disorders:
        return {"series": [], "comparison": {"analyses": [], "leader": None, "summary": ""}, "warnings": ["No valid disorders selected."]}

    if not region_codes:
        region_codes = ["GB"]

    series_list = []
    warnings = []
    multi_disorder = len(disorders) > 1
    multi_region = len(region_codes) > 1

    for disorder in disorders:
        for geo in region_codes:
            payload = retrieve_trends(
                term=disorder["search_term"],
                geo=geo,
                timeframe_value=timeframe_value,
                category=category or disorder.get("gtrends_category", 0),
            )
            if multi_disorder and multi_region:
                label = f"{disorder['name']} ({geo})"
            elif multi_region:
                label = geo
            else:
                label = disorder["name"]

            series_list.append(
                {
                    "label": label,
                    "disorder_id": str(disorder["_id"]),
                    "disorder_name": disorder["name"],
                    "region": geo,
                    "dates": payload["dates"],
                    "values": payload["values"],
                    "source": payload["source"],
                    "sparse": payload.get("sparse", False),
                }
            )
            warnings.extend(payload.get("warnings", []))

    comparison = compare_series(series_list)
    return {
        "series": series_list,
        "comparison": comparison,
        "warnings": list(dict.fromkeys(warnings)),  # de-duplicate, preserve order
    }
