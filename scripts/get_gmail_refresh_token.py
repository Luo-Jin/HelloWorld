#!/usr/bin/env python3
"""Interactive helper to obtain a Gmail OAuth2 refresh token.

Usage:
  - Set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in the environment,
    or enter them when prompted.
  - Run this script. It will open a browser to ask for consent and capture the code.
  - The script exchanges the code for tokens and prints the `refresh_token` and
    an example `export` line you can add to your environment.

Notes:
  - Requires `requests` (already in project requirements).
  - For Gmail SMTP scopes use `https://mail.google.com/`.
"""
import os
import sys
import socket
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse
import requests


def find_free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class CodeHandler(BaseHTTPRequestHandler):
    server_version = "SimpleCodeHandler/0.1"

    def do_GET(self):
        qs = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(qs)
        code = params.get('code', [None])[0]
        error = params.get('error', [None])[0]
        if code:
            self.server.code = code
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Authorization received</h2><p>You can close this tab.</p></body></html>")
        elif error:
            self.server.code = None
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h2>Authorization failed: {error}</h2></body></html>".encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body><h2>No code received.</h2></body></html>")

    def log_message(self, format, *args):
        # reduce console noise
        pass


def main():
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID') or input('Google OAuth client_id: ').strip()
    client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET') or input('Google OAuth client_secret: ').strip()
    if not client_id or not client_secret:
        print('client_id and client_secret are required.')
        sys.exit(1)

    scope = 'https://mail.google.com/'
    # Use a fixed port by default so you can register a single redirect URI in Google
    default_port = int(os.environ.get('GET_GMAIL_PORT', '8080'))
    port = default_port
    redirect_uri = f'http://localhost:{port}/'

    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlparse.urlencode(auth_params)

    server = HTTPServer(('localhost', port), CodeHandler)
    server.code = None

    def run_server():
        server.handle_request()  # handle a single request then return

    print('\nUsing redirect URI:')
    print(redirect_uri)
    print('Please add this exact URI to your OAuth client (Authorized redirect URIs) if you have not already:')
    print(redirect_uri)
    print('\nOpening browser for Google consent...')
    print('If the browser does not open, visit this URL:')
    print(auth_url)
    webbrowser.open(auth_url)

    run_server()

    code = getattr(server, 'code', None)
    if not code:
        print('No code received. Abort.')
        sys.exit(1)

    print('Exchanging code for tokens...')
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    try:
        r = requests.post(token_url, data=data, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print('Token exchange failed:', e)
        print('Response:', getattr(e, 'response', None))
        sys.exit(1)

    tokens = r.json()
    refresh_token = tokens.get('refresh_token')
    access_token = tokens.get('access_token')

    print('\nToken response keys: ' + ','.join(tokens.keys()))
    if not refresh_token:
        print('\nWarning: no refresh_token returned. Make sure you used `access_type=offline` and `prompt=consent` and that this Google account allows issuing refresh tokens.')
    else:
        print('\nRefresh token obtained:')
        print(refresh_token)
        print('\nAdd this to your environment (example):')
        print(f"export MAIL_OAUTH2_REFRESH_TOKEN='{refresh_token}'")
        # Optionally save the refresh token (and client ids) to a .env file in the project root.
        save_env = os.environ.get('SAVE_REFRESH_TO_ENV')
        do_save = None
        if save_env is not None:
            do_save = save_env.lower() in ('1', 'true', 'yes')
        else:
            try:
                ans = input('\nSave refresh token to .env in project root? (y/N): ').strip().lower()
                do_save = ans in ('y', 'yes')
            except Exception:
                do_save = False

        if do_save:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            dotenv_path = os.path.join(project_root, '.env')
            existing = []
            if os.path.exists(dotenv_path):
                with open(dotenv_path, 'r') as f:
                    existing = f.readlines()

            def set_or_append(lines, key, value):
                pref = key + '='
                for i, ln in enumerate(lines):
                    if ln.strip().startswith(key + '=') or ln.strip().startswith('export ' + key + '='):
                        lines[i] = f"export {key}='{value}'\n"
                        return lines
                lines.append(f"export {key}='{value}'\n")
                return lines

            lines = existing
            lines = set_or_append(lines, 'MAIL_OAUTH2_REFRESH_TOKEN', refresh_token)
            if client_id:
                lines = set_or_append(lines, 'MAIL_OAUTH2_CLIENT_ID', client_id)
            if client_secret:
                lines = set_or_append(lines, 'MAIL_OAUTH2_CLIENT_SECRET', client_secret)

            with open(dotenv_path, 'w') as f:
                f.writelines(lines)
            print(f"Saved refresh token and client info to {dotenv_path}")

    if access_token:
        print('\nAccess token (short-lived) also returned; can be used immediately if desired.')


if __name__ == '__main__':
    main()
