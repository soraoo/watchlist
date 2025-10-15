from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user, logout_user, login_user
from sqlalchemy import select

from watchlist.extensions import db
from watchlist.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("无效输入")
            return redirect(url_for("auth.login"))

        user = db.session.execute(select(User).filter_by(username=username)).scalar()
        if user is not None and user.validate_password(password):
            login_user(user)
            flash("登录成功")
            return redirect(url_for("main.index"))

        flash("用户名或密码无效")
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("再见")
    return redirect(url_for("main.index"))


@auth_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        name = request.form.get("name")
        if not name or len(name) > 20:
            flash("无效输入")
            return redirect(url_for("auth.settings"))

        current_user.name = name
        db.session.commit()
        flash("更新成功")
        return redirect(url_for("main.index"))

    return render_template("settings.html")
