from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_DELETE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from controllers import kc_user, kc_group, kc_client, ks_project, os_group, gf_group, ks_user
import xml.etree.ElementTree as elemTree
import time
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
        time.sleep(0.6)
        kc_client.post_admin_access_token()
        kc_group.post_project_name(user_name)
        ks_project.post_project_id(user_name)

    except LDAPException as e:
        response = (" The error is ", e)

    ldap_conn.unbind()
    return response

def add_user(user_name, user_sn, user_gname, user_mail, user_passwd):
    ldap_attr = {}
    ldap_attr['cn'] = user_name
    ldap_attr['sn'] = user_sn
    ldap_attr['givenName'] = user_gname
    ldap_attr['mail'] = user_mail
    ldap_attr['userPassword'] = user_passwd

    ldap_conn = connect_ldap_server()

    user_dn = "cn="+str(user_name)+",ou=users,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        res = check_email(user_mail)
        if res == "mail duplication":
            return "mail"
        response = ldap_conn.add(dn=user_dn,
                                object_class='inetOrgPerson',
                                attributes=ldap_attr)
        if response == False:
            return "user"

        time.sleep(0.6)
        add_group(user_name)

        kc_user.put_email_verified(user_name=user_name)

    except LDAPException as e:
        response = e
    return response

def check_email(user_mail):
    ldap_conn = connect_ldap_server()

    try:
        response = ldap_conn.search("ou=users,cn=admin,dc=devstack,dc=co,dc=kr",
                 "(&(objectClass=person))",
                 attributes=['mail'])
    except LDAPException as e:
        response = e

    entries = ldap_conn.entries
    for entry in entries:
        if entry['mail'] == user_mail:
            return "mail duplication"

    return

def check_user(user_name):
    search_base = 'ou=users,cn=admin,dc=devstack,dc=co,dc=kr'
    search_filter = "(cn="+user_name+")"

    ldap_conn = connect_ldap_server()

    try:
        ldap_conn.search(search_base=search_base,
                         search_filter=search_filter
                         #search_scope=BASE
                         )

        response = ldap_conn.entries
    except LDAPException as e:
        response = e
    return response

def check_group(group_name):
    search_base = 'ou=groups,cn=admin,dc=devstack,dc=co,dc=kr'
    search_filter = "(cn="+group_name+")"

    ldap_conn = connect_ldap_server()
    try:
        ldap_conn.search(search_base=search_base,
                         search_filter=search_filter
                         #search_scope=BASE
                         )
        response = ldap_conn.entries
    except LDAPException as e:
        response = e
    return response

def add_group_member(group_name, user_name):
    ldap_conn = connect_ldap_server()

    group_dn = "cn="+str(group_name)+",ou=groups,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        check = check_user(user_name)
        if len(check) == 0:
            return "user"
        check = check_group(group_name)
        if len(check) == 0:
            return "group"

        response = ldap_conn.modify(group_dn, {'memberUid': [(MODIFY_ADD, [user_name])]})
    except LDAPException as e:
        response = e
    return response

def delete_group_member(group_name, user_name):
    ldap_conn = connect_ldap_server()

    group_dn = "cn="+str(group_name)+",ou=groups,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        check = check_user(user_name)
        if len(check) == 0:
            return "user"
        check = check_group(group_name)
        if len(check) == 0:
            return "group"

        response = ldap_conn.modify(group_dn, {'memberUid': [(MODIFY_DELETE, [user_name])]})
    except LDAPException as e:
        response = e
    return response

def delete_group(user_name):
    ldap_conn = connect_ldap_server()
    roles = ['admin', 'editor', 'viewer']
    for role in roles:
        group_name = user_name+"@"+role
        group_dn = "cn="+group_name+",ou=groups,cn=admin,dc=devstack,dc=co,dc=kr"
        try:
            response = ldap_conn.delete(group_dn)
        except LDAPException as e:
           response = e
    return response

def delete_user(user_name):
    ldap_conn = connect_ldap_server()
    user_dn = "cn="+user_name+",ou=users,cn=admin,dc=devstack,dc=co,dc=kr"

    check = check_user(user_name)
    if len(check) == 0:
        return "user"

    delete_group(user_name)
    ks_project.delete_project(user_name)
    ks_user.delete_user(user_name)

    try:
        response = ldap_conn.delete(user_dn)
    except LDAPException as e:
        response = e
    return response