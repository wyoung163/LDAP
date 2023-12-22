#!/usr/bin/python

import json, os, requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client, ks_auth

url = tree.find('string[@name="KC_URL"]').text
acess_token = ""
user_id = ""

def get_user_id(user_name):
    for i in range(0,len(ks_auth.keystone.users.list())):
        if str(ks_auth.keystone.users.list()[i]).split(",")[5].split("=")[1] == user_name:
            global user_id
            user_id = str(ks_auth.keystone.users.list()[i]).split(",")[3].split("=")[1]
    return user_id

def delete_user(user_name):
    try:
        user_id = get_user_id(user_name)
        print(user_id)
        print(ks_auth.keystone.users.delete(user=user_id))
        return True
    except:
        return False

    #res = os.popen(". /app/openrc && openstack user delete " + user_name).read()