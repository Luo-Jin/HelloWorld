from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


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
    tour = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<School {self.sch_name}>'

