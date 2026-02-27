import os
from flask import Flask, render_template, request
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

    # Import models and create tables
    from . import models
    with app.app_context():
        db.create_all()

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
        from .models import School
        districts = db.session.query(School.sch_district).distinct().filter(School.sch_district.isnot(None)).order_by(School.sch_district).all()
        districts = [d[0] for d in districts if d[0]]
        return render_template('dropdowns.html', districts=districts)

    @app.route('/info')
    def info():
        from .models import School
        district = request.args.get('district', '')
        if district:
            schools = School.query.filter(School.sch_district == district).all()
        else:
            schools = School.query.all()
        return render_template('info.html', schools=schools)

    return app
