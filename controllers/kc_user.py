import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_group

url = tree.find('string[@name="KC_URL"]').text
user_id = ""

# 사용자 id 조회
def get_user_id(user_name):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_group.access_token
    }
    print(user_name)
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users?username="+user_name+"&exact=true", 
                       headers=headers,
                       verify=False)
    print(res.json())
    global user_id
    user_id = res.json()[0].get("id")

# 사용자 이메일 허용 여부 true로 수정
def put_email_verified():
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_group.access_token
    }
    data = {
        "emailVerified": True,
    }
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+user_id, 
                       headers=headers,
                       json=data,
                       verify=False)
    print(res)


def put_user_password(user_passwd):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_group.access_token
    }
    data = {
        "type": "password",
        "value": user_passwd,
        "temporary": False
    }
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+user_id+"/reset-password", 
                       headers=headers,
                       json=data,
                       verify=False)
    print(res)
