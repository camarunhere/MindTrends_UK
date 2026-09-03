from flask_login import current_user, login_required

from flask import current_app, flash, redirect, render_template, request, url_for

from app.admin import admin_bp
from app.models.analysis import ActivityLog, ContentPage, SavedAnalysis
from app.models.disorder import Disorder
from app.models.query_log import SearchQuery
from app.models.settings import Settings
from app.models.user import User
from app.utils.decorators import admin_required


@admin_bp.route("/")
@login_required
@admin_required
def overview():
    stats = {
        "users": User.count(),
        "disorders": Disorder.count(),
        "saved_analyses": SavedAnalysis.count(),
        "queries": SearchQuery.count(),
        "logs": ActivityLog.count(),
    }
    recent_logs = ActivityLog.recent(limit=10)
    return render_template("admin/overview.html", stats=stats, recent_logs=recent_logs)


# ---------------------------------------------------------------- Disorders
@admin_bp.route("/disorders")
@login_required
@admin_required
def disorders():
    items = Disorder.all()
    return render_template("admin/disorders.html", disorders=items)


@admin_bp.route("/disorders/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_disorder():
    if request.method == "POST":
        Disorder.create(
            name=request.form["name"],
            description=request.form["description"],
            search_term=request.form.get("search_term", ""),
            category=request.form.get("category", "Mental Health"),
            gtrends_category=request.form.get("gtrends_category", 0),
        )
        ActivityLog.record("disorder_created", actor=current_user.email, details={"name": request.form["name"]})
        flash("Disorder added.", "success")
        return redirect(url_for("admin.disorders"))
    return render_template("admin/disorder_form.html", disorder=None)


@admin_bp.route("/disorders/<disorder_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_disorder(disorder_id):
    disorder = Disorder.get_by_id(disorder_id)
    if not disorder:
        return render_template("errors/404.html"), 404
    if request.method == "POST":
        Disorder.update(
            disorder_id,
            name=request.form["name"],
            description=request.form["description"],
            search_term=request.form.get("search_term", ""),
            category=request.form.get("category", "Mental Health"),
            gtrends_category=int(request.form.get("gtrends_category", 0) or 0),
            active=request.form.get("active") == "on",
        )
        ActivityLog.record("disorder_updated", actor=current_user.email, details={"id": disorder_id})
        flash("Disorder updated.", "success")
        return redirect(url_for("admin.disorders"))
    return render_template("admin/disorder_form.html", disorder=disorder)


@admin_bp.route("/disorders/<disorder_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_disorder(disorder_id):
    Disorder.delete(disorder_id)
    ActivityLog.record("disorder_deleted", actor=current_user.email, details={"id": disorder_id})
    flash("Disorder deleted.", "info")
    return redirect(url_for("admin.disorders"))


# ------------------------------------------------------------------ Content
@admin_bp.route("/content")
@login_required
@admin_required
def content():
    pages = {key: ContentPage.get(key) for key in ContentPage.all_keys()}
    return render_template("admin/content.html", pages=pages)


@admin_bp.route("/content/<key>", methods=["POST"])
@login_required
@admin_required
def update_content(key):
    if key not in ContentPage.all_keys():
        return render_template("errors/404.html"), 404
    ContentPage.update(key, request.form["title"], request.form["body"])
    ActivityLog.record("content_updated", actor=current_user.email, details={"key": key})
    flash(f"'{key.title()}' page updated.", "success")
    return redirect(url_for("admin.content"))


# -------------------------------------------------------------------- Users
@admin_bp.route("/users")
@login_required
@admin_required
def users():
    items = User.all()
    return render_template("admin/users.html", users=items)


@admin_bp.route("/users/<user_id>/role", methods=["POST"])
@login_required
@admin_required
def update_user_role(user_id):
    user = User.get_by_id(user_id)
    if not user:
        return render_template("errors/404.html"), 404
    user.set_role(request.form["role"])
    ActivityLog.record("user_role_updated", actor=current_user.email, details={"user": user.email, "role": request.form["role"]})
    flash(f"Updated role for {user.email}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.get_by_id(user_id)
    if not user:
        return render_template("errors/404.html"), 404
    user.set_active(not user.is_active)
    ActivityLog.record(
        "user_deactivated" if not user.is_active else "user_reactivated",
        actor=current_user.email,
        details={"user": user.email},
    )
    flash(f"Account {'deactivated' if not user.is_active else 'reactivated'} for {user.email}.", "info")
    return redirect(url_for("admin.users"))


# ------------------------------------------------------- Search parameters
@admin_bp.route("/parameters", methods=["GET", "POST"])
@login_required
@admin_required
def parameters():
    if request.method == "POST":
        names = request.form.getlist("category_name")
        ids = request.form.getlist("category_gtrends_id")
        categories = [
            {"name": n.strip(), "gtrends_id": int(i or 0)}
            for n, i in zip(names, ids) if n.strip()
        ]
        Settings.set_categories(categories)
        ActivityLog.record("categories_updated", actor=current_user.email)
        flash("Search categories updated.", "success")
        return redirect(url_for("admin.parameters"))

    return render_template(
        "admin/parameters.html",
        categories=Settings.get_categories(),
        timeframes=Settings.get_timeframes(),
        regions=current_app.config["UK_REGIONS"],
    )


# ------------------------------------------------------------------- Logs
@admin_bp.route("/logs")
@login_required
@admin_required
def logs():
    entries = ActivityLog.recent(limit=300)
    return render_template("admin/logs.html", logs=entries)


# --------------------------------------------------------- Retrieval config
@admin_bp.route("/retrieval-settings", methods=["GET", "POST"])
@login_required
@admin_required
def retrieval_settings():
    if request.method == "POST":
        Settings.update_retrieval_settings(
            mode=request.form.get("mode"),
            cache_ttl_minutes=int(request.form.get("cache_ttl_minutes") or 60),
            request_timeout=int(request.form.get("request_timeout") or 15),
            max_retries=int(request.form.get("max_retries") or 2),
            backoff_seconds=int(request.form.get("backoff_seconds") or 5),
        )
        ActivityLog.record("retrieval_settings_updated", actor=current_user.email)
        flash("Data retrieval settings updated.", "success")
        return redirect(url_for("admin.retrieval_settings"))

    return render_template("admin/retrieval_settings.html", settings=Settings.get_retrieval_settings())
