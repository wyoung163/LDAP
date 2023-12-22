import requests
import config
from controllers import kc_user, gf_group

url = config.KC_URL #tree.find('string[@name="KC_URL"]').text
access_token = ""

# admin-cli access-token 조회
params = {
    "grant_type": "password",
    "client_secret": config.KC_ADMIN_CLIENT_SECRET,
    "client_id": config.KC_ADMIN_CLIENT_ID,
    "username": config.KC_ADMIN_USERNAME,
    "password": config.KC_ADMIN_PASSWD,
    "scope": "openid"
}
def post_admin_access_token():
    res = requests.post(url+"realms/master/protocol/openid-connect/token", 
                        data=params,
                        verify=False)
    #print(res.json())
    global access_token
    access_token = res.json().get("access_token")

# client id 조회
def get_client_id(clientId):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    res = requests.get(url+"admin/realms/"+config.KC_REALM+"/clients?clientId="+clientId,
                       headers=headers,
                       verify=False)
    client_id = res.json()[0].get("id")
    return client_id 