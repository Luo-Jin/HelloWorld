#!/usr/bin/env python3
"""Script to exercise the registration flow and report whether the app attempted a real send.

It will create the app using current environment config, register a temporary user,
capture `app.logger` output, and print whether the email was sent via SMTP/OAuth2
or only logged as a verification link.
"""
import io
import logging
import time
import sys
import os
import smtplib
# ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

# Use default smtplib.SMTP behavior (no forced debug output)


def main():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})

    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    with app.app_context():
        client = app.test_client()
        ts = int(time.time())
        username = f'testsender{ts}'
        email = f'{username}@example.com'
        resp = client.post('/register', data={
            'username': username,
            'email': email,
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }, follow_redirects=True)

    # Flush logs
    handler.flush()
    log_text = buf.getvalue()
    print('--- app logger output ---')
    print(log_text)

    if 'Sent verification email to' in log_text:
        print('RESULT: Email was SENT via SMTP/OAuth2 (see log above).')
    elif 'Verification link for' in log_text or 'Verification link' in log_text:
        print('RESULT: Verification link was LOGGED (no SMTP configured or send failed).')
    else:
        print('RESULT: No verification log found; check app logger configuration.')


if __name__ == '__main__':
    main()
