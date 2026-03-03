import os
from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
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
        tour_param = request.args.get('tour', '')
        
        query = School.query
        
        if region:
            query = query.filter(School.sch_region == region)
        
        if school_type:
            query = query.filter(School.sch_type == school_type)
        
        if tour_param:
            if tour_param.lower() in ['1','true','yes','y']:
                query = query.filter(School.tour.is_(True))
            elif tour_param.lower() in ['0','false','no','n']:
                query = query.filter(School.tour.is_(False))
        
        schools = query.all()
        return render_template('info.html', schools=schools)

    @app.route('/students')
    def students():
        from .models import Student
        students = Student.query.order_by(Student.stu_name).all()
        return render_template('students.html', students=students)

    @app.route('/students/new', methods=['GET', 'POST'])
    def new_student():
        from .models import Student
        if request.method == 'POST':
            name = request.form.get('stu_name')
            birth = request.form.get('stu_birth')
            gender = request.form.get('stu_gender')
            email = request.form.get('stu_email')
            phone = request.form.get('stu_phone')
            dob = None
            if birth:
                try:
                    dob = datetime.date.fromisoformat(birth)
                except Exception:
                    dob = None
            s = Student(stu_name=name, stu_birth=dob, stu_gender=gender, stu_email=email, stu_phone=phone)
            db.session.add(s)
            db.session.commit()
            return redirect(url_for('students'))
        return render_template('student_form.html', student=None)

    @app.route('/students/<int:stu_id>/edit', methods=['GET', 'POST'])
    def edit_student(stu_id):
        from .models import Student
        s = Student.query.get_or_404(stu_id)
        if request.method == 'POST':
            s.stu_name = request.form.get('stu_name')
            birth = request.form.get('stu_birth')
            if birth:
                try:
                    s.stu_birth = datetime.date.fromisoformat(birth)
                except Exception:
                    s.stu_birth = None
            s.stu_gender = request.form.get('stu_gender')
            s.stu_email = request.form.get('stu_email')
            s.stu_phone = request.form.get('stu_phone')
            db.session.commit()
            return redirect(url_for('students'))
        return render_template('student_form.html', student=s)

    @app.route('/students/<int:stu_id>/delete', methods=['POST'])
    def delete_student(stu_id):
        from .models import Student
        s = Student.query.get_or_404(stu_id)
        db.session.delete(s)
        db.session.commit()
        return redirect(url_for('students'))

    return app
