import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_user
from controllers import gf_group

url = tree.find('string[@name="KC_URL"]').text
access_token = ""
client_id = ""

# admin-cli access-token 조회
params = {
    "grant_type": "password",
    "client_secret": tree.find('string[@name="KC_ADMIN_CLIENT_SECRET"]').text,
    "client_id": tree.find('string[@name="KC_ADMIN_CLIENT_ID"]').text,
    "username": tree.find('string[@name="KC_ADMIN_USERNAME"]').text,
    "password": tree.find('string[@name="KC_ADMIN_PASSWD"]').text,
    "scope": "openid"
}
def post_admin_access_token():
    res = requests.post(url+"realms/master/protocol/openid-connect/token", 
                        data=params,
                        verify=False)
    #print(res.json())
    global access_token
    access_token = res.json().get("access_token")
    return

# Openstack client id 조회
def get_client_id():
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/clients?clientId="+tree.find('string[@name="KC_OS_CLIENT_ID"]').text,
                       headers=headers,
                       verify=False)
    global client_id
    client_id = res.json()[0].get("id")
    return