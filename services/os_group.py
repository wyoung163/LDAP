import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client, kc_group

url = tree.find('string[@name="KC_URL"]').text
client_id = ""
role_id = ""
role_name = ""

# openstack client role 조회
def get_client_role():
    global client_id
    client_id = kc_client.get_client_id(tree.find('string[@name="KC_OS_CLIENT_ID"]').text)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/clients/"+client_id+"/roles?search=member",
                       headers=headers, 
                       verify=False)
    global role_name, role_id
    role_id = res.json()[0].get("id")
    role_name = res.json()[0].get("name")

# openstack (member) role mapping
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
    res = requests.post(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups/"+kc_group.group_id+"/role-mappings/clients/"+client_id,
                        headers=headers,
                        json=data,
                        verify=False)