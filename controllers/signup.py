from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError
import os
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('keys.xml')

def connect_ldap_server():
    try:
        server_uri = tree.find('string[@name="LDAP_URL"]').text
        server = Server(server_uri, get_info=ALL)
        connection = Connection(server,
                        user=tree.find('string[@name="LDAP_ADMIN_DN"]').text,
                        password=tree.find('string[@name="LDAP_PASSWD"]').text)
        bind_response = connection.bind() 
    except LDAPBindError as e:
        connection = e
    print(bind_response)
    return connection

def add_group(user_name):
    ldap_attr = {}
    ldap_attr['objectClass'] = ['top', 'posixGroup']
    new_gid = tree.find('string[@name="LDAP_NEW_GID"]').text

    ldap_conn = connect_ldap_server()

    try:
        ldap_attr['gidNumber'] = str(int(new_gid) + 1)
        response = ldap_conn.add('cn='+user_name+'@editor'+',ou=groups,cn=admin,dc=devstack,dc=co,dc=kr',
                                    attributes=ldap_attr)
        ldap_attr['gidNumber'] = str(int(new_gid) + 2)
        response = ldap_conn.add('cn='+user_name+'@viewer'+',ou=groups,cn=admin,dc=devstack,dc=co,dc=kr',
                                    attributes=ldap_attr)
        ldap_attr['gidNumber'] = new_gid
        ldap_attr['memberUid'] = user_name
        response = ldap_conn.add('cn='+user_name+'@admin'+',ou=groups,cn=admin,dc=devstack,dc=co,dc=kr',
                                    attributes=ldap_attr)

        #os.environ['LDAP_NEW_GID'] = str(int(os.getenv('LDAP_NEW_GID')) + 3);
    except LDAPException as e:
        response = (" The error is ", e)

    ldap_conn.unbind()
    print(response)
    return response

def add_user(user_name, user_sn, user_mail, user_passwd):
    ldap_attr = {}
    ldap_attr['cn'] = user_name 
    ldap_attr['sn'] = user_sn 
    #ldap_attr['givenName'] = user_gname
    ldap_attr['mail'] = user_mail
    #ldap_attr['userPassword'] = os.getenv('LDAP_NEW_USER_PASSWD')

    ldap_conn = connect_ldap_server()
    
    user_dn = "cn="+str(user_name)+",ou=users,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        response = ldap_conn.add(dn=user_dn,
                                object_class='inetOrgPerson',
                                attributes=ldap_attr)
        add_group(user_name)

    except LDAPException as e:
        response = e
    print(response)
    return response