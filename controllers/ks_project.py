#!/usr/bin/python

import json, os, requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client

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
    domain_id = os.popen(". /app/openrc && echo ${OS_KC_DOMAIN_ID}").read()
    #domain_id = os.popen(". /opt/stack/federation/LDAP/openrc && echo ${OS_KC_DOMAIN_ID}").read()
    res = os.popen(". /app/openrc && openstack project create " + project_name + " --domain "+domain_id).read()
    #res = os.popen(". /opt/stack/federation/LDAP/openrc && openstack project create " + project_name + " --domain "+domain_id).read()

def get_project_id(project_name):
    res = os.popen(". /app/openrc && openstack project show " + project_name + " --format json --column id").read()
    #res = os.popen(". /opt/stack/federation/LDAP/openrc && openstack project show " + project_name + " --format json --column id").read()
    project_id = json.loads(res).get("id")
    return project_id

def post_project_id(project_name):
    kc_client.post_admin_access_token()
    post_project(project_name)
    project_id = get_project_id(project_name)
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
    res = os.popen(". /app/openrc && openstack project delete " + project_name).read()
    #res = os.popen(". /opt/stack/federation/LDAP/openrc && openstack project delete " + project_name).read()