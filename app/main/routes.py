from flask import render_template

from app.main import main_bp
from app.models.analysis import ContentPage
from app.models.disorder import Disorder
from app.services.analysis_service import analyse_series
from app.services.trends_service import retrieve_trends


@main_bp.route("/")
def home():
    disorders = Disorder.all(active_only=True)
    return render_template("main/home.html", disorders=disorders)


@main_bp.route("/about")
def about():
    page = ContentPage.get("about")
    return render_template("main/content_page.html", page=page, active="about")


@main_bp.route("/methodology")
def methodology():
    page = ContentPage.get("methodology")
    return render_template("main/content_page.html", page=page, active="methodology")


@main_bp.route("/faq")
def faq():
    page = ContentPage.get("faq")
    return render_template("main/content_page.html", page=page, active="faq")


@main_bp.route("/resources")
def resources():
    page = ContentPage.get("resources")
    return render_template("main/content_page.html", page=page, active="resources")


@main_bp.route("/disorders")
def disorders():
    items = Disorder.all(active_only=True)
    return render_template("main/disorders.html", disorders=items)


@main_bp.route("/disorders/<slug>")
def disorder_detail(slug):
    disorder = Disorder.get_by_slug(slug)
    if not disorder:
        return render_template("errors/404.html"), 404
    return render_template("main/disorder_detail.html", disorder=disorder)


@main_bp.route("/trends-overview")
def trends_overview():
    """Explore Public Trend Summary — a lightweight, no-login overview."""
    disorders = Disorder.all(active_only=True)[:6]
    summaries = []
    for d in disorders:
        payload = retrieve_trends(
            term=d["search_term"], geo="GB", timeframe_value="today 12-m",
            category=d.get("gtrends_category", 0),
        )
        insight = analyse_series(d["name"], payload["dates"], payload["values"])
        summaries.append(
            {
                "disorder": d,
                "dates": payload["dates"],
                "values": payload["values"],
                "source": payload["source"],
                "insight": insight,
            }
        )
    return render_template("main/trends_overview.html", summaries=summaries)
