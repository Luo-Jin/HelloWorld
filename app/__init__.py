import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import text
import smtplib
from email.message import EmailMessage
import datetime
import requests
import base64

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

    # Mail configuration (can be provided via environment variables)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    try:
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '25'))
    except ValueError:
        app.config['MAIL_PORT'] = 25
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'False').lower() in ('1', 'true', 'yes')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    # OAuth2 SMTP settings (optional)
    app.config['MAIL_OAUTH2_REFRESH_TOKEN'] = os.environ.get('MAIL_OAUTH2_REFRESH_TOKEN')
    app.config['MAIL_OAUTH2_CLIENT_ID'] = os.environ.get('MAIL_OAUTH2_CLIENT_ID')
    app.config['MAIL_OAUTH2_CLIENT_SECRET'] = os.environ.get('MAIL_OAUTH2_CLIENT_SECRET')

    db.init_app(app)

    # Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'home'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Token helpers for email verification
    def _get_serializer():
        return URLSafeTimedSerializer(app.config['SECRET_KEY'])

    def generate_confirmation_token(email):
        s = _get_serializer()
        return s.dumps(email, salt='email-confirm')

    def confirm_token(token, expiration=60*60*24):
        s = _get_serializer()
        try:
            email = s.loads(token, salt='email-confirm', max_age=expiration)
        except Exception:
            return None
        return email

    def send_verification_email(to_email, token):
        link = url_for('verify_email', token=token, _external=True)
        mail_server = app.config.get('MAIL_SERVER')
        subject = 'Please verify your email'
        # plain text fallback
        body = f'Please verify your email by visiting the following link:\n\n{link}\n\nIf you did not request this, ignore this email.'
        # render HTML template
        try:
            html_body = render_template('emails/verify.html', link=link, user_email=to_email)
        except Exception:
            html_body = None

        # Try OAuth2 (refresh-token) first if configured
        oauth2_refresh = app.config.get('MAIL_OAUTH2_REFRESH_TOKEN')
        oauth2_client_id = app.config.get('MAIL_OAUTH2_CLIENT_ID')
        oauth2_client_secret = app.config.get('MAIL_OAUTH2_CLIENT_SECRET')

        def _get_oauth2_access_token(refresh_token, client_id, client_secret):
            try:
                resp = requests.post('https://oauth2.googleapis.com/token', data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                }, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                return data.get('access_token')
            except Exception as e:
                app.logger.warning('Failed to obtain OAuth2 access token: %s', e)
                return None

        if mail_server and oauth2_refresh and oauth2_client_id and oauth2_client_secret:
            try:
                access_token = _get_oauth2_access_token(oauth2_refresh, oauth2_client_id, oauth2_client_secret)
                if access_token:
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
                    msg['To'] = to_email
                    msg.set_content(body)
                    if html_body:
                        msg.add_alternative(html_body, subtype='html')
                    port = app.config.get('MAIL_PORT', 25)
                    use_tls = app.config.get('MAIL_USE_TLS', False)
                    username = app.config.get('MAIL_USERNAME')
                    # Connect and authenticate using XOAUTH2
                    server = smtplib.SMTP(mail_server, port, timeout=10)
                    server.ehlo()
                    if use_tls:
                        server.starttls()
                        server.ehlo()
                    # build XOAUTH2 auth string
                    auth_str = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
                    auth_b64 = base64.b64encode(auth_str.encode()).decode()
                    code, resp_str = server.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
                    if code != 235:
                        raise RuntimeError(f'SMTP XOAUTH2 auth failed: {code} {resp_str}')
                    server.send_message(msg)
                    server.quit()
                    app.logger.info('Sent verification email to %s via OAuth2 SMTP', to_email)
                    app.logger.info('Verification link for %s: %s', to_email, link)
                    return True
            except Exception as e:
                app.logger.warning('OAuth2 SMTP send failed: %s', e)
                # fallthrough to username/password method or logging

        if mail_server:
            try:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
                msg['To'] = to_email
                msg.set_content(body)
                if html_body:
                    msg.add_alternative(html_body, subtype='html')
                port = app.config.get('MAIL_PORT', 25)
                use_tls = app.config.get('MAIL_USE_TLS', False)
                username = app.config.get('MAIL_USERNAME')
                password = app.config.get('MAIL_PASSWORD')
                if use_tls:
                    server = smtplib.SMTP(mail_server, port, timeout=10)
                    server.starttls()
                else:
                    server = smtplib.SMTP(mail_server, port, timeout=10)
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
                server.quit()
                app.logger.info('Sent verification email to %s', to_email)
                app.logger.info('Verification link for %s: %s', to_email, link)
                return True
            except Exception as e:
                app.logger.warning('Failed to send email via SMTP: %s', e)
                # fallback to logging below
        # Fallback: log the link and HTML body so developer can copy it
        app.logger.info('Verification link for %s: %s', to_email, link)
        if html_body:
            app.logger.debug('Verification HTML for %s: %s', to_email, html_body)
        return False

    # Import models and create tables
    from . import models
    with app.app_context():
        db.create_all()
        # Ensure new columns exist in SQLite (add if missing) using SQLAlchemy 2.0 API
        try:
            with db.engine.connect() as conn:
                inspector = conn.execute(text("PRAGMA table_info('user')")).all()
                cols = [row[1] for row in inspector]
                if 'confirmed' not in cols:
                    conn.execute(text("ALTER TABLE user ADD COLUMN confirmed BOOLEAN NOT NULL DEFAULT 0"))
                    app.logger.info('Added confirmed column to user table')
                if 'confirmed_at' not in cols:
                    conn.execute(text("ALTER TABLE user ADD COLUMN confirmed_at DATETIME NULL"))
                    app.logger.info('Added confirmed_at column to user table')
        except Exception:
            # If anything goes wrong, continue; app will log errors elsewhere
            app.logger.exception('Could not ensure user columns')

        # Ensure `admin` user is marked confirmed (useful for initial deployments)
        try:
            from .models import User
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user and not getattr(admin_user, 'confirmed', False):
                admin_user.confirmed = True
                admin_user.confirmed_at = datetime.datetime.utcnow()
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info('Marked admin user as confirmed')
        except Exception:
            app.logger.exception('Could not auto-confirm admin user')

    @app.route('/', methods=['GET', 'POST'])
    def home():
        # login page as default — authenticate admin User
        from .models import User
        if request.method == 'POST':
            name = request.form.get('stu_name','').strip()
            pwd = request.form.get('password','').strip()
            if not name or not pwd:
                flash('Username and password are required.')
                return render_template('login.html')

            user = User.query.filter_by(username=name).first()
            if user and user.check_password(pwd):
                if not getattr(user, 'confirmed', False):
                    flash('Please verify your email before logging in. Check your email for the verification link.')
                    return render_template('login.html')
                login_user(user)
                return redirect(url_for('index'))

            flash('Invalid username or password.')
            return render_template('login.html')
        return render_template('login.html')

    @app.route('/index')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        from .models import User
        if request.method == 'POST':
            username = request.form.get('username','').strip()
            email = request.form.get('email','').strip()
            password = request.form.get('password','')
            password2 = request.form.get('password2','')
            errors = []
            if not username:
                errors.append('Username is required.')
            if not email:
                errors.append('Email is required.')
            if not password:
                errors.append('Password is required.')
            if password != password2:
                errors.append('Passwords do not match.')
            if User.query.filter_by(username=username).first():
                errors.append('Username already exists.')
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered.')
            if errors:
                for e in errors:
                    flash(e)
                return render_template('register.html')
            u = User(username=username, email=email)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            # generate verification token and send email (or log link)
            token = generate_confirmation_token(u.email)
            send_verification_email(u.email, token)
            flash('Account created. A verification email has been sent. Please verify your email before logging in.')
            return redirect(url_for('home'))
        return render_template('register.html')

    # student registration route removed

    @app.route('/hello')
    def hello():
        return 'Hello, world!'

    @app.route('/verify/<token>')
    def verify_email(token):
        from .models import User
        email = confirm_token(token)
        if not email:
            flash('The verification link is invalid or has expired.')
            return redirect(url_for('home'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.')
            return redirect(url_for('home'))
        if getattr(user, 'confirmed', False):
            flash('Account already verified. Please log in.')
            return redirect(url_for('home'))
        user.confirmed = True
        user.confirmed_at = datetime.datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('Your account has been verified. You can now log in.')
        return redirect(url_for('home'))

    @app.route('/banner')
    @login_required
    def banner():
        return render_template('banner.html')

    @app.route('/dropdowns')
    @login_required
    def dropdowns():
        from .models import School
        regions = db.session.query(School.sch_region).distinct().filter(School.sch_region.isnot(None)).order_by(School.sch_region).all()
        regions = [r[0] for r in regions if r[0]]
        school_types = db.session.query(School.sch_type).distinct().filter(School.sch_type.isnot(None)).order_by(School.sch_type).all()
        school_types = [t[0] for t in school_types if t[0]]
        return render_template('dropdowns.html', regions=regions, school_types=school_types)

    @app.route('/admin/users')
    @login_required
    def admin_users():
        # Only allow the admin user to access
        if not (current_user.is_authenticated and getattr(current_user, 'username', '') == 'admin'):
            abort(403)
        from .models import User
        users = User.query.order_by(User.id).all()
        return render_template('admin_users.html', users=users)

    @app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
    @login_required
    def admin_delete_user(user_id):
        # Only admin can delete; disallow deleting admin account
        if not (current_user.is_authenticated and getattr(current_user, 'username', '') == 'admin'):
            abort(403)
        from .models import User
        user = User.query.get(user_id)
        if not user:
            flash('User not found.')
            return redirect(url_for('admin_users'))
        if user.username == 'admin':
            flash('Cannot delete the admin account.')
            return redirect(url_for('admin_users'))
        try:
            db.session.delete(user)
            db.session.commit()
            flash(f'User {user.username} deleted.')
        except Exception:
            db.session.rollback()
            flash('Failed to delete user.')
        return redirect(url_for('admin_users'))

    @app.route('/info')
    @login_required
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
        # supply region and type lists for dropdowns when rendering combined page
        regions = db.session.query(School.sch_region).distinct().filter(School.sch_region.isnot(None)).order_by(School.sch_region).all()
        regions = [r[0] for r in regions if r[0]]
        school_types = db.session.query(School.sch_type).distinct().filter(School.sch_type.isnot(None)).order_by(School.sch_type).all()
        school_types = [t[0] for t in school_types if t[0]]
        return render_template('school.html', schools=schools, regions=regions, school_types=school_types, selected_region=region, selected_type=school_type, selected_tour=tour_param)

    # student CRUD pages removed

    return app
