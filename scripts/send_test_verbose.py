#!/usr/bin/env python3
import os
import sys
import requests
import smtplib
import base64
import json
import traceback
from email.message import EmailMessage

# Load .env if present (simple loader)
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
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)

recipient = 'luojin.roge@gmail.com'
client_id = os.getenv('MAIL_OAUTH2_CLIENT_ID')
client_secret = os.getenv('MAIL_OAUTH2_CLIENT_SECRET')
refresh_token = os.getenv('MAIL_OAUTH2_REFRESH_TOKEN')
username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')
mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
mail_port = int(os.getenv('MAIL_PORT', '587'))
use_tls = (os.getenv('MAIL_USE_TLS') or '1').lower() in ('1', 'true', 'yes')
from_addr = os.getenv('MAIL_DEFAULT_SENDER') or username or f'noreply@{os.uname().nodename}'

print('Preparing to send test email to', recipient)
print('Using server', mail_server, 'port', mail_port, 'use_tls=', use_tls)
print('MAIL_USERNAME present:', bool(username))
print('MAIL_OAUTH2_CLIENT_ID present:', bool(client_id))
print('MAIL_OAUTH2_REFRESH_TOKEN present:', bool(refresh_token))

msg = EmailMessage()
msg['Subject'] = 'Test email from flask_app'
msg['From'] = from_addr
msg['To'] = recipient
msg.set_content('This is a test email sent by an automated script.')

# Try OAuth2 XOAUTH2 if possible
if client_id and client_secret and refresh_token and username:
    try:
        print('\nExchanging refresh token for access token...')
        r = requests.post('https://oauth2.googleapis.com/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }, timeout=15)
        print('token status', r.status_code)
        try:
            print('token response:', r.text)
            j = r.json()
        except Exception:
            j = None
        r.raise_for_status()
        access = j.get('access_token') if isinstance(j, dict) else None
        if access:
            print('Got access token (len):', len(access))
            print('Attempting SMTP XOAUTH2 auth and send...')
            s = smtplib.SMTP(mail_server, mail_port, timeout=30)
            s.set_debuglevel(1)
            s.ehlo()
            if use_tls:
                s.starttls()
                s.ehlo()
            auth_str = f"user={username}\x01auth=Bearer {access}\x01\x01"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()
            try:
                code, resp = s.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
                print('AUTH response code:', code)
                print('AUTH response:', resp)
            except Exception as e:
                print('AUTH docmd raised:', e)
                traceback.print_exc()
                s.quit()
                raise
            if code != 235:
                print('XOAUTH2 auth failed, aborting XOAUTH2 path')
                s.quit()
            else:
                s.send_message(msg)
                print('Email sent via XOAUTH2 SMTP')
                s.quit()
                sys.exit(0)
    except Exception as e:
        print('XOAUTH2 path error:', e)
        traceback.print_exc()

# Fallback to username/password SMTP
if username and password:
    try:
        print('\nAttempting username/password SMTP auth and send...')
        s = smtplib.SMTP(mail_server, mail_port, timeout=30)
        s.set_debuglevel(1)
        s.ehlo()
        if use_tls:
            s.starttls()
            s.ehlo()
        s.login(username, password)
        s.send_message(msg)
        print('Email sent via username/password SMTP')
        s.quit()
        sys.exit(0)
    except Exception as e:
        print('Username/password SMTP failed:', e)
        traceback.print_exc()

print('No valid SMTP credentials available or send failed.')
sys.exit(2)
