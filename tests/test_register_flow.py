import re

import pytest


def test_registration_and_email_verification_flow(client, caplog):
    """Register a user, capture the logged verification link, and verify the account."""
    caplog.set_level('INFO')

    resp = client.post('/register', data={
        'username': 'flowuser',
        'email': 'flowuser@example.com',
        'password': 'Password1!',
        'password2': 'Password1!'
    }, follow_redirects=True)

    # registration should redirect back to home and include a flash about verification
    assert resp.status_code == 200

    # capture the verification link from app logs (fallback path in send_verification_email)
    log_text = '\n'.join(r.message for r in caplog.records)
    m = re.search(r'/verify/([^\s\)\"]+)', log_text)
    assert m, f'No verification link found in logs:\n{log_text}'
    token = m.group(1)

    # call the verify endpoint
    verify_resp = client.get(f'/verify/{token}', follow_redirects=True)
    assert verify_resp.status_code == 200
    assert b'Your account has been verified' in verify_resp.data
