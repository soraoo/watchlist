from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import select

from watchlist.extensions import db
from watchlist.models import Movie, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("main.index"))
        title = request.form.get("title").strip()
        year = request.form.get("year").strip()
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("无效输入")
            return redirect(url_for("main.index"))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("创建成功")
        return redirect(url_for("main.index"))

    movies = db.session.execute(select(Movie)).scalars().all()
    return render_template("index.html", movies=movies)


@main_bp.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
@login_required
def edit(movie_id: int):
    movie = db.get_or_404(Movie, movie_id)
    if request.method == "POST":
        title = request.form.get("title").strip()
        year = request.form.get("year").strip()
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("无效输入")
            return redirect(url_for("main.edit", movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash("修改成功")
        return redirect(url_for("main.index"))

    return render_template("edit.html", movie=movie)


@main_bp.route("/movie/delete/<int:movie_id>", methods=["POST"])
@login_required
def delete(movie_id: int):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("main.index"))
