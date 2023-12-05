import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_user, kc_client, gf_group

url = tree.find('string[@name="KC_URL"]').text
role_id = ""
role_name = ""
group_id = ""
group_name = ""
gf_role = ""

# role group(admin, editor, viewer) 조회
def get_group(user_name):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    roles = ['admin', 'editor', 'viewer']
    for role in roles:
        res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups?search="+user_name+"@"+role,
                       headers=headers,
                       verify=False)
        global gf_role
        gf_role = role
        global group_name, group_id
        group_id = res.json()[0].get("id")
        group_name = res.json()[0].get("name")
        get_client_role()
        put_group_attribute(user_name=user_name)
        kc_user.get_user_id(user_name=user_name)
        put_join_group(user_name=user_name) 
        post_group_role_mapping() #openstack role mapping
        gf_group.post_group_role_mapping() #grafana role mapping

# openstack client role 조회
def get_client_role():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/clients/"+kc_client.client_id+"/roles?search=member",
                       headers=headers, 
                       verify=False)
    global role_name, role_id
    role_id = res.json()[0].get("id")
    role_name = res.json()[0].get("name")

# group attribute에 project name 추가
def put_group_attribute(user_name):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
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

# 사용자 group member로 join
def put_join_group(user_name):
    kc_user.get_user_id(user_name)
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+kc_user.user_id+"/groups/"+group_id, 
                       headers=headers,
                       verify=False)
    
# openstack (member) role mapping
def post_group_role_mapping():
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    data = [{
        "id": role_id,
        "name": role_name
    }]
    res = requests.post(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups/"+group_id+"/role-mappings/clients/"+kc_client.client_id,
                        headers=headers,
                        json=data,
                        verify=False)