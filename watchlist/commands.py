import click
from flask import Flask
from sqlalchemy import select

from watchlist.extensions import db
from watchlist.models import User, Movie


def register_commands(app: Flask):
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
