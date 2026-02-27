import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        try:
            os.makedirs(app.instance_path, exist_ok=True)
        except OSError:
            pass
    else:
        app.config.update(test_config)

    db.init_app(app)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/hello')
    def hello():
        return 'Hello, world!'

    @app.route('/banner')
    def banner():
        return render_template('banner.html')

    @app.route('/dropdowns')
    def dropdowns():
        return render_template('dropdowns.html')

    @app.route('/info')
    def info():
        return render_template('info.html')

    return app
