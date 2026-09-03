from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.models.analysis import ActivityLog
from app.models.user import ROLE_RESEARCHER, User


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.email_exists(form.email.data):
            flash("An account with that email already exists. Please log in instead.", "danger")
        else:
            user = User.create(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                role=ROLE_RESEARCHER,
                institution=form.institution.data,
            )
            ActivityLog.record("user_registered", actor=user.email)
            login_user(user)
            flash("Welcome! Your researcher account has been created.", "success")
            return redirect(url_for("dashboard.home"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            ActivityLog.record("user_login", actor=user.email)
            next_url = request.args.get("next")
            flash(f"Welcome back, {user.name.split(' ')[0]}.", "success")
            return redirect(next_url or url_for("dashboard.home"))
        if user and not user.is_active:
            flash("This account has been deactivated. Contact an administrator.", "danger")
        else:
            flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    ActivityLog.record("user_logout", actor=current_user.email)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
