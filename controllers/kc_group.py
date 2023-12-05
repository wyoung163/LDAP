import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_user
from controllers import gf_group

url = tree.find('string[@name="KC_URL"]').text
access_token = ""
client_id = ""
role_id = ""
role_name = ""
group_id = []
group_name = []
user_id = ""

# admin-cli access-token
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

def get_group(user_name):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    roles = ['admin', 'editor', 'viewer']
    for role in roles:
        res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups?search="+user_name+"@"+role,
                       headers=headers,
                       verify=False)
        print(res.json())
        global group_name, group_id
        group_id = res.json()[0].get("id")
        group_name = res.json()[0].get("name")
        put_group_attribute(user_name=user_name)
        get_user_id(user_name=user_name)
        put_join_group(user_name=user_name)
        gf_group.client_id(group_id, role)
        post_group_role_mapping()

def get_client_role():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/clients/"+client_id+"/roles?search=member",
                       headers=headers, 
                       verify=False)
    global role_name, role_id
    role_id = res.json()[0].get("id")
    role_name = res.json()[0].get("name")

def put_group_attribute(user_name):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    data = {
        "name": group_name,
        "attributes": {
            "project_name": [
                user_name
            ]
        }
    }
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups/"+group_id, 
                       headers=headers,
                       json=data,
                       verify=False)
    print(res)

def get_user_id(user_name):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    print(user_name)
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users?username="+user_name+"&exact=true", 
                       headers=headers,
                       verify=False)
    print(res.json())
    global user_id
    user_id = res.json()[0].get("id")

def put_join_group(user_name):
    get_user_id(user_name)
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+user_id+"/groups/"+group_id, 
                       headers=headers,
                       verify=False)
    print("join", res)


def post_group_role_mapping():
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token 
    }
    data = [{
        "id": role_id,
        "name": role_name
    }]
    res = requests.post(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups/"+group_id+"/role-mappings/clients/"+client_id,
                        headers=headers,
                        json=data,
                        verify=False)
    print(res)