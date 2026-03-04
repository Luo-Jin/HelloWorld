#!/usr/bin/env python3
# Load .env into environment (support lines starting with 'export ')
import os
import sys
import logging
from datetime import datetime
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                if k.startswith('export '):
                    k = k[len('export '):]
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)

# Enable smtplib debug output by wrapping SMTP
import smtplib
_OrigSMTP = smtplib.SMTP
class _DebugSMTP(_OrigSMTP):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.set_debuglevel(1)
smtplib.SMTP = _DebugSMTP

from app import create_app, db

app = create_app()
# ensure we run with app context
with app.app_context():
    # attach console handler to app logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    client = app.test_client()
    username = f'testuser_{int(datetime.utcnow().timestamp())}'
    email = 'luojin.roge@gmail.com'
    password = 'TestPass123!'
    print('Posting register for', username, email)
    resp = client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'password2': password
    }, follow_redirects=True)
    print('Status code:', resp.status_code)
    if b'verification email' in resp.data or b'Account created' in resp.data:
        print('Register response indicates email sent or logged')
    # verify user in DB
    User = app.models.User if hasattr(app, 'models') else None
    try:
        from app.models import User
        u = User.query.filter_by(email=email).order_by(User.id.desc()).first()
        if u:
            print('User created:', u.username, 'confirmed=', getattr(u, 'confirmed', None))
        else:
            print('User not found in DB')
    except Exception as e:
        print('DB check failed:', e)
