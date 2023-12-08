#!/usr/bin/python

import json, os, requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')
from controllers import kc_client

url = tree.find('string[@name="KC_URL"]').text
acess_token = ""

def delete_user(user_name):
    res = os.popen(". /app/openrc && openstack user delete " + user_name).read()
    #res = os.popen(". /opt/stack/federation/LDAP/openrc && openstack user delete " + user_name).read()