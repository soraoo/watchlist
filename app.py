from pathlib import Path

import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Path(app.root_path)}/data.db"

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


@app.route("/")
def index():
    movies = db.session.execute(select(Movie)).scalars().all()
    return render_template("index.html", movies=movies)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
