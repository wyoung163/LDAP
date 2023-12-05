import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_group

url = tree.find('string[@name="KC_URL"]').text
client_id = ""
role_id = ""
role_name = ""

# grfana client id 조회
def get_client_id():
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_group.access_token
    }
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/clients?clientId="+tree.find('string[@name="KC_GF_CLIENT_ID"]').text,
                       headers=headers,
                       verify=False)
    global client_id
    client_id = res.json()[0].get("id")
    get_client_role()

# grafana client role(projectAdmin, projectEditor, projectViewer) 조회
def get_client_role():
    role = kc_group.gf_role
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_group.access_token
    }
    if role == "admin":
        gf_role = "projectAdmin"
    elif role == "editor": 
        gf_role = "projectEditor"
    else: 
        gf_role = "projectViewer"

    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/clients/"+client_id+"/roles?search="+gf_role,
                    headers=headers, 
                    verify=False)
    global role_name, role_id
    role_id = res.json()[0].get("id")
    role_name = res.json()[0].get("name")
    post_group_role_mapping()

# 각 role group에 role mapping
def post_group_role_mapping():
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_group.access_token 
    }
    data = [{
        "id": role_id,
        "name": role_name
    }]
    res = requests.post(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups/"+kc_group.group_id+"/role-mappings/clients/"+client_id,
                        headers=headers,
                        json=data,
                        verify=False)