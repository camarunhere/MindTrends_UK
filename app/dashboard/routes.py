from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.dashboard import dashboard_bp
from app.models.analysis import ActivityLog, SavedAnalysis
from app.models.disorder import Disorder
from app.models.query_log import SearchQuery
from app.models.settings import Settings
from app.services.export_service import build_pdf_report, series_to_csv
from app.services.query_service import run_query


@dashboard_bp.route("/dashboard")
@login_required
def home():
    disorders = Disorder.all(active_only=True)
    regions = current_app.config["UK_REGIONS"]
    timeframes = Settings.get_timeframes()
    recent = SavedAnalysis.for_user(current_user.id, limit=5)
    return render_template(
        "dashboard/explore.html",
        disorders=disorders,
        regions=regions,
        timeframes=timeframes,
        recent=recent,
    )


@dashboard_bp.route("/dashboard/query", methods=["POST"])
@login_required
def query():
    payload = request.get_json(force=True, silent=True) or {}
    disorder_ids = payload.get("disorder_ids") or []
    region_codes = payload.get("regions") or ["GB"]
    timeframe_value = payload.get("timeframe") or "today 12-m"
    category = int(payload.get("category") or 0)

    if not disorder_ids:
        return jsonify({"error": "Select at least one mental health disorder."}), 400

    result = run_query(disorder_ids, region_codes, timeframe_value, category)
    SearchQuery.record(current_user.id, disorder_ids, region_codes, timeframe_value, category)
    ActivityLog.record(
        "trend_query",
        actor=current_user.email,
        details={"disorders": len(disorder_ids), "regions": region_codes, "timeframe": timeframe_value},
    )
    return jsonify(result)


@dashboard_bp.route("/dashboard/save", methods=["POST"])
@login_required
def save_analysis():
    payload = request.get_json(force=True, silent=True) or {}
    title = (payload.get("title") or "Untitled analysis").strip()
    params = payload.get("params") or {}
    summary = payload.get("summary") or {}

    SavedAnalysis.create(current_user.id, title, params, summary)
    ActivityLog.record("analysis_saved", actor=current_user.email, details={"title": title})
    return jsonify({"ok": True})


@dashboard_bp.route("/dashboard/history")
@login_required
def history():
    analyses = SavedAnalysis.for_user(current_user.id, limit=100)
    return render_template("dashboard/history.html", analyses=analyses)


@dashboard_bp.route("/dashboard/history/<analysis_id>")
@login_required
def history_detail(analysis_id):
    analysis = SavedAnalysis.get(analysis_id, user_id=current_user.id)
    if not analysis:
        return render_template("errors/404.html"), 404

    params = analysis["params"]
    result = run_query(
        params.get("disorder_ids", []),
        params.get("regions", ["GB"]),
        params.get("timeframe", "today 12-m"),
        params.get("category", 0),
    )
    return render_template("dashboard/history_detail.html", analysis=analysis, result=result)


@dashboard_bp.route("/dashboard/history/<analysis_id>/delete", methods=["POST"])
@login_required
def delete_analysis(analysis_id):
    SavedAnalysis.delete(analysis_id, current_user.id)
    flash("Saved analysis deleted.", "info")
    return redirect(url_for("dashboard.history"))


@dashboard_bp.route("/dashboard/export/csv", methods=["POST"])
@login_required
def export_csv():
    payload = request.get_json(force=True, silent=True) or {}
    series_list = payload.get("series") or []
    csv_bytes = series_to_csv(series_list)
    ActivityLog.record("export_csv", actor=current_user.email)
    return (
        csv_bytes,
        200,
        {
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=mindtrends_export.csv",
        },
    )


@dashboard_bp.route("/dashboard/export/pdf", methods=["POST"])
@login_required
def export_pdf():
    payload = request.get_json(force=True, silent=True) or {}
    series_list = payload.get("series") or []
    params = payload.get("params") or {}
    insights = [s["insight"] for s in payload.get("analyses") or []]

    pdf_bytes = build_pdf_report("MindTrends UK — Analysis Report", params, series_list, insights)
    ActivityLog.record("export_pdf", actor=current_user.email)
    return (
        pdf_bytes,
        200,
        {
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment; filename=mindtrends_report.pdf",
        },
    )
