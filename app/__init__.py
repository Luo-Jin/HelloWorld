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
        regions = db.session.query(School.sch_region).distinct().filter(School.sch_region.isnot(None)).order_by(School.sch_region).all()
        regions = [r[0] for r in regions if r[0]]
        school_types = db.session.query(School.sch_type).distinct().filter(School.sch_type.isnot(None)).order_by(School.sch_type).all()
        school_types = [t[0] for t in school_types if t[0]]
        return render_template('dropdowns.html', regions=regions, school_types=school_types)

    @app.route('/info')
    def info():
        from .models import School
        region = request.args.get('region', '')
        school_type = request.args.get('school_type', '')
        
        query = School.query
        
        if region:
            query = query.filter(School.sch_region == region)
        
        if school_type:
            query = query.filter(School.sch_type == school_type)
        
        schools = query.all()
        return render_template('info.html', schools=schools)

    return app
