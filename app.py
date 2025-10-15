from pathlib import Path

import click
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Path(app.root_path)}/data.db"
app.config["SECRET_KEY"] = "dev"

db = SQLAlchemy(app, model_class=Base)


class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))


class Movie(db.Model):
    __tablename__ = "movie"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    year: Mapped[str] = mapped_column(String(4))


@app.cli.command("init-db")
@click.option("--drop", is_flag=True, help="Drop然后Create.")
def init_database(drop: bool):
    if drop:
        db.drop_all()
        click.echo("数据库销毁完成.")
    db.create_all()
    click.echo("数据库创建完成.")


@app.cli.command()
def forge():
    click.echo("开始生成测试数据...")

    db.drop_all()
    db.create_all()

    name = "soraoo"
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo("生成完毕。")


@app.context_processor
def inject_user():
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title").strip()
        year = request.form.get("year").strip()
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("无效输入")
            return redirect(url_for("index"))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("创建成功")
        return redirect(url_for("index"))

    movies = db.session.execute(select(Movie)).scalars().all()
    return render_template("index.html", movies=movies)


@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
def edit(movie_id: int):
    movie = db.get_or_404(Movie, movie_id)
    if request.method == "POST":
        title = request.form.get("title").strip()
        year = request.form.get("year").strip()
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("无效输入")
            return redirect(url_for("edit", movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash("修改成功")
        return redirect(url_for("index"))

    return render_template("edit.html", movie=movie)


@app.route("/movie/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id: int):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
