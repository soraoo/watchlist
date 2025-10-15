from pathlib import Path
from typing import Optional

import click
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Path(app.root_path)}/data.db"
app.config["SECRET_KEY"] = "dev"

db = SQLAlchemy(app, model_class=Base)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password: str):
        return check_password_hash(self.password_hash, password)


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

    user = User(name=name, username="soraoo")
    user.set_password("123456")
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo("生成完毕。")


@app.cli.command()
@click.option("--username", prompt=True, help="登录用户名")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="登录密码")
def admin(username: str, password: str):
    db.create_all()

    user = db.session.execute(select(User)).scalar()
    if user is not None:
        click.echo("更新用户...")
        user.username = username
        user.set_password(password)
    else:
        click.echo("创建用户...")
        user = User(username=username, name="Admin")
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo("完成")


@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    return user


@app.context_processor
def inject_user():
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("index"))
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
@login_required
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
@login_required
def delete(movie_id: int):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("无效输入")
            return redirect(url_for("login"))

        user = db.session.execute(select(User).filter_by(username=username)).scalar()
        if user is not None and user.validate_password(password):
            login_user(user)
            flash("登录成功")
            return redirect(url_for("index"))

        flash("用户名或密码无效")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("再见")
    return redirect(url_for("index"))


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        name = request.form.get("name")
        if not name or len(name) > 20:
            flash("无效输入")
            return redirect(url_for("settings"))

        current_user.name = name
        db.session.commit()
        flash("更新成功")
        return redirect(url_for("index"))

    return render_template("settings.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
