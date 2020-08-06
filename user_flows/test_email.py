import requests
import json
import jwt
import time
import os

notification_url = os.getenv("notification_url")
api_secret = os.getenv("NOTIFICATION_SECRET")

if(not api_secret):
    raise ValueError("Missing secret environment variable")

if(not notification_url):
    raise ValueError("Missing url")


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

def get_service_jwt(api_key_secret, service_id):
    jwtSecret = api_key_secret
    header = {'typ': 'JWT', 'alg': 'HS256'}
    combo = {}
    currentTimestamp = int(time.time())
    data = {
        'iss': service_id,
        'iat': currentTimestamp,
    }
    combo.update(data)
    combo.update(header)
    encoded_jwt = jwt.encode(combo, jwtSecret, algorithm='HS256')
    return encoded_jwt


def get_authenticated_request(endpoint):
    jwt = get_jwt()
    header = {"Authorization": "Bearer " + jwt.decode("utf-8")}
    r = requests.get(notification_url + endpoint, headers=header)
    return r


def get_status():
    r = requests.get(notification_url + "/_status")
    return r


def get_organizations():
    return get_authenticated_request("/organisations")


def get_organization_id(data):
    id = data[-1]['id']
    for organization in data:
        if organization['count_of_live_services'] >= 1:
            id = organization['id']
    return id


def get_services():
    return get_authenticated_request("/service")


def get_services_id(data):
    service_id = data[-1]['id']
    for service in data:
        if service['email_from'] == "solutions":
            service_id = service['id']
    return service_id


def get_users():
    return get_authenticated_request("/user")


def get_user_id(users, service_id):
    user_id = users[-1]['id']
    for user in users:
        if service_id in user['services']:
            user_id = user['id']
    return user_id


def get_templates(service_id):
    return get_authenticated_request("/service/" + service_id + "/template")


def get_template_id(templates, service_id):
    template_id = templates[-1]["id"]
    for template in templates:
        if template["service"] == service_id and template["template_type"] == "email":
            template_id = template["id"]
    return template_id


def test_status():
    assert get_status().status_code == 200


def create_api_key(service_id, user_id):
    jwt = get_jwt()
    header = {"Authorization": "Bearer " + jwt.decode("utf-8"), 'Content-Type': 'application/json'}
    payload = json.dumps({"created_by": user_id, "key_type": "normal", "name": "userflows"})
    r = requests.post(notification_url + "/service/" + service_id + "/api-key", headers=header, data=payload)
    return r


def get_api_key(service_id):
    return get_authenticated_request("/service/" + service_id + "/api-keys")


def get_right_api_key(get_key_response):
    right_key = get_key_response[-1]["id"]
    for api_key in get_key_response:
        if api_key["name"] == "userflows" and api_key["expiry_date"] == None:
            right_key = api_key["id"]
    return right_key


def revoke_key(old_key_id, service_id):
    jwt = get_jwt()
    header = {"Authorization": "Bearer " + jwt.decode("utf-8"), 'Content-Type': 'application/json'}
    r = requests.post(notification_url + "/service/" + service_id + "/api-key/revoke/" + old_key_id, headers=header, data={})
    return r


def send_email(jwt, template_id):
    header = {"Authorization": "Bearer " + jwt.decode("utf-8"), 'Content-Type': 'application/json'}
    payload = json.dumps({"template_id": template_id, "email_address": "shutchin@thoughtworks.com"})
    r = requests.post(notification_url + "/v2/notifications/email", headers=header, data=payload)
    return r


def get_notification_id(notification_response):
    return notification_response.json()['id']


def get_notification_status(jwt, notification_id):
    header = {"Authorization": "Bearer " + jwt.decode("utf-8"), 'Content-Type': 'application/json'}
    r = requests.get(notification_url + "/v2/notifications/" + notification_id, headers=header)
    return r


def test_email():
    organizations = get_organizations()
    assert organizations.status_code == 200
    services = get_services()
    assert services.status_code == 200
    service_id = get_services_id(services.json()['data'])
    users = get_users()
    assert users.status_code == 200
    user_id = get_user_id(users.json()['data'], service_id)
    templates = get_templates(service_id)
    template_id = get_template_id(templates.json()['data'], service_id)
    assert templates.status_code == 200
    old_key = get_api_key(service_id)
    assert old_key.status_code == 200
    old_key_id = get_right_api_key(old_key.json()["apiKeys"])
    response = revoke_key(old_key_id, service_id)
    assert response.status_code == 202
    service_key = create_api_key(service_id, user_id)
    assert service_key.status_code == 201
    service_jwt = get_service_jwt(service_key.json()["data"], service_id)
    email_response = send_email(service_jwt, template_id)
    assert email_response.status_code == 201
    notification_id = get_notification_id(email_response)
    time_count = 0
    notification_status = ""
    while notification_status != "sending" and time_count < 30:
      notification_status_response = get_notification_status(service_jwt, notification_id)
      assert notification_status_response.status_code == 200
      notification_status = notification_status_response.json()['status']
      time.sleep(1)
      time_count = time_count + 1
    assert notification_status == 'sending'
