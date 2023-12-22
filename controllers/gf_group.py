import requests
import config
from controllers import kc_client, kc_group

url = config.KC_URL 
client_id = ""
role_id = ""
role_name = ""

# grafana client role(projectAdmin, projectEditor, projectViewer) 조회
def get_client_role():
    global client_id
    client_id = kc_client.get_client_id(config.KC_GF_CLIENT_ID)
    role = kc_group.gf_role
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }
    if role == "admin":
        gf_role = "projectAdmin"
    elif role == "editor": 
        gf_role = "projectEditor"
    else: 
        gf_role = "projectViewer"

    res = requests.get(url+"admin/realms/"+config.KC_REALM+"/clients/"+client_id+"/roles?search="+gf_role,
                    headers=headers, 
                    verify=False)
    global role_name, role_id
    role_id = res.json()[0].get("id")
    role_name = res.json()[0].get("name")

# 각 role group에 role mapping
def post_group_role_mapping():
    get_client_role()
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    data = [{
        "id": role_id,
        "name": role_name
    }]
    res = requests.post(url+"admin/realms/"+config.KC_REALM+"/groups/"+kc_group.group_id+"/role-mappings/clients/"+client_id,
                        headers=headers,
                        json=data,
                        verify=False)