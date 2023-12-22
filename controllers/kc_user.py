import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client

url = tree.find('string[@name="KC_URL"]').text
id = ""

# 사용자 id 조회
def get_user_id(user_id):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }
    try:
        res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users?username="+user_id+"&exact=true", 
                       headers=headers,
                       verify=False)
        global id
        id = res.json()[0].get("id")
        return True
    except:
        return False

# 사용자 이메일 허용 여부 true로 수정
def put_email_verified(user_id):
    isSuccess = get_user_id(user_id)
    if isSuccess == False:
        return False
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }
    data = {
        "emailVerified": True,
    }
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+id,
                       headers=headers,
                       json=data,
                       verify=False)
    return True


# 사용자의 기존 user attribute 조회
def get_user_attributes(user_id):
    isSuccess = get_user_id(user_id)
    if isSuccess == False:
        return False
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }
    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+id, 
                       headers=headers,
                       verify=False)
    print(res.json().get("attributes"))
    attributes = res.json().get("attributes")
    return attributes
    
# 사용자의 attribute로 system_role:true|false 지정
def post_user_attributes(user_id, isUser):
    isSuccess = get_user_id(user_id)
    #attributes = get_user_attributes(user_name)
    #if attributes == False: 
    #    return False
    
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }

    data = ""
    # dn = attributes["LDAP_ENTRY_DN"]
    # id = attributes["LDAP_ID"]
    # create_time = attributes["createTimestamp"]
    # modify_time = attributes["modifyTimestamp"]

    if isUser:
        data = {
            "attributes": {
                "system_admin": [
                    "false"
                ]
            }
        }
    else: 
        data = {
            "attributes": {
                "system_admin": [
                   "true"
                ]
            }
        }

    # data["attributes"]["LDAP_ENTRY_DN"] = dn
    # data["attributes"]["LDAP_ID"] = id
    # data["attributes"]["create_time"] = create_time
    # data["attributes"]["modify_time"] = modify_time
        
    res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+id, 
                       headers=headers,
                       json=data,
                       verify=False)
    if res.status_code >= 400:
        return False
    return True

# 사용자 password 수정 <불필요>
# def put_user_password(user_passwd):
#     headers = {
#        "Content-Type": "application/json",
#         "Authorization": "Bearer " + kc_client.access_token
#     }
#     data = {
#         "type": "password",
#         "value": user_passwd,
#         "temporary": False
#     }
#     res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/users/"+user_id+"/reset-password", 
#                        headers=headers,
#                        json=data,
#                        verify=False)
