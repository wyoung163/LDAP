#!/usr/bin/python

import json, os, requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client, kc_group

# keystone-auth-cli
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
import config
# Keystone server 연결
auth = v3.Password(auth_url=config.KS_URL,
        username=config.KS_ADMIN_USERNAME,
        password=config.KS_ADMIN_PASSWORD,
        system_scope="all",
        user_domain_id=config.KS_USER_DOMAIN_ID)
sess = session.Session(auth=auth)
keystone = client.Client(session=sess)

url = tree.find('string[@name="KC_URL"]').text
acess_token = ""
group_id = ""
group_name = ""

def get_groups(user_name, role):
    headers = {
       "Content-Type": "application/json",
        "Authorization": "Bearer " + kc_client.access_token
    }

    res = requests.get(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups?search="+user_name+"@"+role+"&exact=true",
                       headers=headers,
                       verify=False)
    global group_name, group_id
    group_id = res.json()[0].get("id")
    group_name = res.json()[0].get("name")

def post_project(project_name):
    ## python-keystoneclient 활용
    proj = keystone.projects.create(name=project_name, domain=config.KS_DOMAIN, enabled=True)
    global project_id
    project_id = str(proj).split(",")[3].split("=")[1]
    return project_id
    ## openstackclient 활용
    #domain_id = os.popen(". /app/openrc && echo ${OS_KC_DOMAIN_ID}").read()
    #res = os.popen(". /app/openrc && openstack project create " + project_name + " --domain "+domain_id).read()

## openstackclient 활용
# def get_project_id(project_name):
#     res = os.popen(". /app/openrc && openstack project show " + project_name + " --format json --column id").read()
#     project_id = json.loads(res).get("id")
#     return project_id

def post_project_id(project_name):
    kc_client.post_admin_access_token()
    post_project(project_name)

    ## openstackclient 활용
    #project_id = get_project_id(project_name)
    roles = ['admin', 'editor', 'viewer']

    for role in roles:
        get_groups(project_name, role)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + kc_client.access_token
        }
        data = {
            "name": group_name,
            "attributes": {
                "project_name": [
                    project_name
                ],
                "project_id": [
                    project_id
                ],
            }
        }
        res = requests.put(url+"admin/realms/"+tree.find('string[@name="KC_REALM"]').text+"/groups/"+group_id,
                       headers=headers,
                       json=data,
                       verify=False)
    return res

def delete_project(project_name):
    project_id = kc_group.get_project_id(project_name)
    keystone.projects.delete(project=project_id)
    ## openstackclient 활용
    #res = os.popen(". /app/openrc && openstack project delete " + project_name).read()

def delete_project(project_name):
    project_id = kc_group.get_project_id(project_name)
    keystone.projects.delete(project=project_id)
    ## openstackclient 활용
    #res = os.popen(". /app/openrc && openstack project delete " + project_name).read()

def put_user_to_project(project_name, user_name):
    ## openstackclient 활용
    res = os.popen(". /app/openrc && openstack role add --project " + project_name + " --user " + user_name + " member").read()

def delete_user_from_project(project_name, user_name):
    ## openstackclient 활용
    res = os.popen(". /app/openrc && openstack role remove --project " + project_name + " --user " + user_name + " member").read()