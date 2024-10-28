from ...db import models
from ...db import crud
from ...core.security import verify_password, generate_totp_secret

import pyotp 
from string import digits, ascii_letters, punctuation

from urllib.parse import urlencode

from ...conftest import get_new_username

import random

def test_register(test_client, test_db):
    username = get_new_username(test_db)
    password = ''.join(random.choices(digits + ascii_letters + punctuation, k=32))

    response = test_client.post("/auth/register", json={
        "username": username, 
        "password": password,
    })

    assert response.status_code == 200, response.json()
    
    data = response.json()

    assert "access_token" in data, 'access_token not in response'
    assert "token_type" in data, 'token_type not in response'
    assert data["token_type"] == "bearer", 'not a bearer token'
    assert isinstance(data["access_token"], str), 'access_token is not string'
    assert len(data["access_token"]) > 10, 'access_token is too short'

    access_token = data["access_token"]

    
    userobj = crud.get_user(test_db, username=username)

    assert isinstance(userobj, models.User), 'user object not User'
    assert verify_password(password, userobj.hashed_password), 'hashed password is wrong'

    assert crud.delete_user(test_db, username=username), f'Deleting {username} failed'

def test_register_with_existing_user(test_client, get_db_username_password_token):
    test_db, username, password, token = get_db_username_password_token

    response = test_client.post("/auth/register", json={
        "username": username, 
        "password": password,
    })

    assert response.status_code == 409, f'expected status code 409 but got {response.json()}'



def test_token(test_client, get_db_username_password_token):
    test_db, username, password, token = get_db_username_password_token
    request_form = dict(
        grant_type="password", 
        username=username, 
        password=password,
        scope="", 
        client_id=None, 
        client_secret=token
    )
    response = test_client.post("/auth/token", data=request_form)
    
    # Assert the response is successful
    assert response.status_code == 200, response.json()

    # Parse the response JSON
    data = response.json()

    # Validate the token and token type
    assert "access_token" in data, "access_token not in response"
    assert "token_type" in data, "token_type not in response"
    assert data["token_type"] == "bearer", "not a bearer token"
    assert isinstance(data["access_token"], str), "access_token is not a string"
    assert len(data["access_token"]) > 10, "access_token is too short"


def test_enable_2fa(test_client, get_db_username_password_token):
    test_db, username, password, token = get_db_username_password_token

    request_form = dict(
        grant_type="password", 
        username=username, 
        password=password,
        scope="", 
        client_id=None, 
        client_secret=token
    )
    response = test_client.post("/auth/enable-2fa", data=request_form, headers=dict(Authorization="Bearer " + token))
    
    # Assert the response is successful
    assert response.status_code == 200, f'{response.status_code} {response.json()}'

    # Parse the response JSON
    data = response.json()

    assert "provisioning_uri" in data, "provisioning uri not in response"
    assert "qr_code_base64" in data, "qr code base64 not in response"
    assert data["provisioning_uri"], "provisioning uri is empty string"
    assert data["qr_code_base64"], "qr code base64 is empty string"

def test_verify_2fa(test_client, get_db_username_password_token):
    test_db, username, password, token = get_db_username_password_token

    # 1. Set up TOTP for the user
    totp_secret = generate_totp_secret()
    user = crud.get_user(test_db, username)
    user.totp_secret = totp_secret
    test_db.add(user)
    test_db.commit()

    # 2. Generate a valid OTP
    valid_otp = pyotp.TOTP(totp_secret).now()

    query_bit = urlencode({ "username": username, "otp": valid_otp },)

    # 3. Verify the 2FA using the OTP
    response = test_client.post(f"/auth/verify-2fa?{query_bit}",)

    # 4. Check that the response is successful
    assert response.status_code == 200, f'status code should be 200, is {response.status_code} {response.content}'

    # Parse and verify the response JSON
    data = response.json()

    assert "access_token" in data, "access_token not in response"
    assert "token_type" in data, "token_type not in response"
    assert data["token_type"] == "bearer", "not a bearer token"
    assert isinstance(data["access_token"], str), "access_token is not a string"
    assert len(data["access_token"]) > 10, "access_token is too short"

    # Test with an invalid OTP
    query_bit = urlencode({ "username": username, "otp": "invalid_otp" },)

    # 3. Verify the 2FA using the OTP
    response = test_client.post(f"/auth/verify-2fa?{query_bit}",)

    assert response.status_code == 401, "Invalid OTP should return 401"

