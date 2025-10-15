from flask import render_template, Flask


def register_errors(app: Flask):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404
