#!/usr/bin/env python3
"""Exchange refresh token for access token and test SMTP AUTH XOAUTH2 against Gmail.

Reads env vars from the environment (sourcing .env before running is recommended).
"""
import os
import sys
import requests
import smtplib
import base64


def getenv(name):
    v = os.getenv(name)
    return v


def main():
    client_id = getenv('MAIL_OAUTH2_CLIENT_ID')
    client_secret = getenv('MAIL_OAUTH2_CLIENT_SECRET')
    refresh_token = getenv('MAIL_OAUTH2_REFRESH_TOKEN')
    username = getenv('MAIL_USERNAME')
    mail_server = getenv('MAIL_SERVER') or 'smtp.gmail.com'
    mail_port = int(getenv('MAIL_PORT') or 587)
    use_tls = (getenv('MAIL_USE_TLS') or '1').lower() in ('1', 'true', 'yes')

    print('vars present:', 'client_id' if client_id else '', 'client_secret' if client_secret else '', 'refresh_token' if refresh_token else '', 'username' if username else '')
    if not (client_id and client_secret and refresh_token and username):
        print('Missing required env variables: ensure MAIL_OAUTH2_CLIENT_ID, MAIL_OAUTH2_CLIENT_SECRET, MAIL_OAUTH2_REFRESH_TOKEN, MAIL_USERNAME are set')
        return 2

    try:
        print('\nRequesting access token via refresh token...')
        r = requests.post('https://oauth2.googleapis.com/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }, timeout=15)
        print('token status', r.status_code)
        print(r.text)
        r.raise_for_status()
        access = r.json().get('access_token')
        if not access:
            print('No access_token in response; aborting')
            return 3

        print('\nAttempting SMTP XOAUTH2 auth to', mail_server, mail_port)
        s = smtplib.SMTP(mail_server, mail_port, timeout=10)
        s.set_debuglevel(1)
        s.ehlo()
        if use_tls:
            s.starttls()
            s.ehlo()

        auth_str = f"user={username}\x01auth=Bearer {access}\x01\x01"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        code, resp = s.docmd('AUTH', 'XOAUTH2 ' + auth_b64)
        print('\nAUTH response:', code, resp)
        if code == 235:
            print('XOAUTH2 authentication succeeded')
            result = 0
        else:
            print('XOAUTH2 authentication failed')
            result = 4
        try:
            s.quit()
        except Exception:
            pass
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
