#!/usr/bin/python

import json, os, requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client, ks_auth

url = tree.find('string[@name="KC_URL"]').text
acess_token = ""
id = ""

def get_user_id(user_id):
    for i in range(0,len(ks_auth.keystone.users.list())):
        if str(ks_auth.keystone.users.list()[i]).split(",")[5].split("=")[1] == user_id:
            global id
            id = str(ks_auth.keystone.users.list()[i]).split(",")[3].split("=")[1]
    return id

def delete_user(user_id):
    try:
        id = get_user_id(user_id)
        print(user_id)
        print(ks_auth.keystone.users.delete(user=id))
        return True
    except:
        return False

    #res = os.popen(". /app/openrc && openstack user delete " + user_name).read()