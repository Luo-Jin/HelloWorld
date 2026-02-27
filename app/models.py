from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class School(db.Model):
    sch_id = db.Column(db.Integer, primary_key=True)
    sch_name = db.Column(db.String(200), nullable=False)
    sch_desc = db.Column(db.Text, nullable=True)
    sch_addr = db.Column(db.String(500), nullable=True)
    sch_email = db.Column(db.String(120), nullable=True)
    sch_logo = db.Column(db.String(500), nullable=True)  # URL or file path to logo
    sch_eoi = db.Column(db.Integer, nullable=True)  # Equity Index (lower = higher socioeconomic advantage)
    sch_decile = db.Column(db.Integer, nullable=True)  # Decile rating 1-10 (historical)
    sch_homepage = db.Column(db.String(500), nullable=True)  # School website URL
    sch_district = db.Column(db.String(100), nullable=True)  # School district/local board area

    def __repr__(self):
        return f'<School {self.sch_name}>'
