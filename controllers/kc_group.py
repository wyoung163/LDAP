import requests
from controllers import kc_user, kc_client, gf_group, os_group, kc_group
import config

url = config.KC_URL
role_id = ""
role_name = ""
group_id = ""
group_name = ""
gf_role = ""

# role group(admin, editor, viewer) 조회
def get_group(user_id):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    roles = ['admin', 'editor', 'viewer']
    for role in roles:
        res = requests.get(url+"admin/realms/"+config.KC_REALM+"/groups?search="+user_id+"@"+role,
                       headers=headers,
                       verify=False)
        global gf_role
        gf_role = role
        global group_name, group_id

        # sync 지연으로 오류가 종종 발생하는 지점 > 예외 처리
        if len(res.json()) < 1:
            return False
        
        group_id = res.json()[0].get("id")
        group_name = res.json()[0].get("name")
        kc_user.get_user_id(user_id)
        kc_group.post_project_name(user_id)
        os_group.post_group_role_mapping() #openstack role mapping
        gf_group.post_group_role_mapping() #grafana role mapping
    
    return True

# group attribute에 project name 추가
def post_project_name(user_id):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    data = {
        "name": group_name,
        "attributes": {
            "project_name": [
                user_id
            ]
        }
    }
    res = requests.put(url+"admin/realms/"+config.KC_REALM+"/groups/"+group_id, 
                       headers=headers,
                       json=data,
                       verify=False)

# 사용자 group member로 join
def put_join_group(user_id):
    kc_user.get_user_id(user_id)
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token 
    }
    res = requests.put(url+"admin/realms/"+config.KC_REALM+"/users/"+kc_user.user_id+"/groups/"+group_id, 
                       headers=headers,
                       verify=False)
    
# project_id 조회를 위한 특정 KC group id 조회
def get_group_id(user_id):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }
    res = requests.get(url+"admin/realms/"+config.KC_REALM+"/groups?search="+user_id+"@admin",
                       headers=headers,
                       verify=False)
    global group_name, group_id
    group_id = res.json()[0].get("id")
    group_name = res.json()[0].get("name")

# KC group의 attribute, project_id 조회
def get_project_id(project_name):
    kc_client.post_admin_access_token()
    get_group_id(project_name)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }
    res = requests.get(url+"admin/realms/"+config.KC_REALM+"/groups/"+group_id,
            headers=headers,
            verify=False)
    #print(res.json().get("attributes").get("project_id")[0])
    project_id = res.json().get("attributes").get("project_id")[0]
    return project_id

    
