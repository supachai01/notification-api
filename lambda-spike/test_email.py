import time
import os

from steps import get_organizations


notification_url = os.getenv("notification_url")
api_secret = os.getenv("NOTIFICATION_SECRET")

if(not api_secret):
    raise ValueError("Missing secret environment variable")

if(not notification_url):
    raise ValueError("Missing url")

def get_organizations():
    return get_authenticated_request("/organisations")

def get_authenticated_request(endpoint):
    jwt = get_jwt()
    header = {"Authorization": "Bearer " + jwt.decode("utf-8")}
    r = requests.get(notification_url + endpoint, headers=header)
    return r

def get_jwt():
    jwtSecret = api_secret
    header = {'typ': 'JWT', 'alg': 'HS256'}
    combo = {}
    currentTimestamp = int(time.time())
    data = {
        'iss': "notify-admin",
        'iat': currentTimestamp,
        'exp': currentTimestamp + 30,
        'jti': 'jwt_nonce'
    }
    combo.update(data)
    combo.update(header)
    encoded_jwt = jwt.encode(combo, jwtSecret, algorithm='HS256')
    return encoded_jwt


def handler(event, context):
    organizations = get_organizations()
    assert organizations.status_code == 200
