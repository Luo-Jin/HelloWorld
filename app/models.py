from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Role(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(80), unique=True, nullable=False)
    role_desc = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Role {self.role_name}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # User lock/unlock status
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=True)

    # Relationship to Role
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Student(db.Model):
    stu_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)  # M, F, Other
    passport_number = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('students', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Student {self.name}>'


class School(db.Model):
    sch_id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Ministry of Education School ID
    sch_name = db.Column(db.String(200), nullable=False)
    sch_desc = db.Column(db.Text, nullable=True)
    sch_addr = db.Column(db.String(500), nullable=True)
    sch_email = db.Column(db.String(120), nullable=True)
    sch_logo = db.Column(db.String(500), nullable=True)  # URL or file path to logo
    sch_eoi = db.Column(db.Integer, nullable=True)  # Equity Index (lower = higher socioeconomic advantage)
    sch_decile = db.Column(db.Integer, nullable=True)  # Decile rating 1-10 (historical)
    sch_homepage = db.Column(db.String(500), nullable=True)  # School website URL
    sch_district = db.Column(db.String(100), nullable=True)  # School district/local board area
    sch_region = db.Column(db.String(50), nullable=True)  # Auckland major sector (North Shore, Central, East, South, West, Rural)
    sch_type = db.Column(db.String(100), nullable=True)  # School type (e.g., Full Primary, Contributing, Secondary)
    tour = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<School {self.sch_name}>'


class SchoolStats(db.Model):
    """School statistics including ethnic demographics."""
    stat_id = db.Column(db.Integer, primary_key=True)
    sch_id = db.Column(db.Integer, db.ForeignKey('school.sch_id'), nullable=False, unique=True)
    
    # Ethnic ratios (percentages)
    ethnic_european_pct = db.Column(db.Float, nullable=True)  # European/Pakeha
    ethnic_maori_pct = db.Column(db.Float, nullable=True)  # Maori
    ethnic_pacific_pct = db.Column(db.Float, nullable=True)  # Pacific Islander
    ethnic_asian_pct = db.Column(db.Float, nullable=True)  # Asian
    ethnic_other_pct = db.Column(db.Float, nullable=True)  # Other
    
    # Additional statistics
    total_students = db.Column(db.Integer, nullable=True)
    male_pct = db.Column(db.Float, nullable=True)
    female_pct = db.Column(db.Float, nullable=True)
    
    # Data source and timestamp
    year = db.Column(db.Integer, nullable=True)  # Statistics year (e.g., 2024)
    data_source = db.Column(db.String(200), nullable=True)  # Where the data came from
    last_updated = db.Column(db.DateTime, nullable=True)  # When the data was last updated
    
    # Relationship to School
    school = db.relationship('School', backref=db.backref('stats', lazy=True, uselist=False))

    def __repr__(self):
        return f'<SchoolStats {self.sch_id}>'

