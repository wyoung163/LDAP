from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_DELETE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from controllers import kc_user, kc_group, kc_client, ks_project, ks_user
import time
import config

def connect_ldap_server():
    try:
        server_uri = config.LDAP_URL
        server = Server(server_uri, get_info=ALL)
        connection = Connection(server,
                        user=config.LDAP_ADMIN_DN,
                        password=config.LDAP_PASSWD)
        bind_response = connection.bind()
    except LDAPBindError as e:
        connection = e
    return connection

def add_group(user_id):
    ldap_attr = {}
    ldap_attr['objectClass'] = ['top', 'posixGroup']
    new_gid = config.LDAP_NEW_GID

    ldap_conn = connect_ldap_server()

    try:
        ldap_attr['gidNumber'] = str(int(new_gid) + 1)
        response = ldap_conn.add('cn='+user_id+'@editor'+',ou=groups,cn=admin,dc=devstack,dc=co,dc=kr',
                                    attributes=ldap_attr)
        ldap_attr['gidNumber'] = str(int(new_gid) + 2)
        response = ldap_conn.add('cn='+user_id+'@viewer'+',ou=groups,cn=admin,dc=devstack,dc=co,dc=kr',
                                    attributes=ldap_attr)
        ldap_attr['gidNumber'] = new_gid
        ldap_attr['memberUid'] = user_id
        response = ldap_conn.add('cn='+user_id+'@admin'+',ou=groups,cn=admin,dc=devstack,dc=co,dc=kr',
                                    attributes=ldap_attr)
        time.sleep(0.6)
        kc_client.post_admin_access_token()
        # 종종 sync가 늦어서 아직 그룹이 등록되지 않았을 때 오류가 발생하는 지점 > 예외 처리 
        isSuccess = kc_group.get_group(user_id)
        if isSuccess == False:
            # 사용자가 회원가입을 동일하게 재진행할 수 있도록 LDAP의 group, user 삭제
            delete_group(user_id)
            delete_user(user_id)
            return False
        kc_group.post_project_name(user_id)
        ks_project.post_project_id(user_id)

    except LDAPException as e:
        response = (" The error is ", e)

    ldap_conn.unbind()
    return response

def add_user(user_id, user_name, mail, passwd, isUser):
    ldap_attr = {}
    ldap_attr['cn'] = user_id
    ldap_attr['sn'] = user_name
    ldap_attr['mail'] = mail
    ldap_attr['userPassword'] = passwd

    ldap_conn = connect_ldap_server()

    user_dn = "cn="+str(user_id)+",ou=users,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        res = check_email(mail)
        if res == "mail duplication":
            return "mail"
        response = ldap_conn.add(dn=user_dn,
                                object_class='inetOrgPerson',
                                attributes=ldap_attr)
        if response == False:
            return "user"

        time.sleep(0.6)
        isSuccess = add_group(user_id)
        if isSuccess == 409:
            return 409

        # 종종 sync가 늦어서 아직 그룹이 등록되지 않았을 때 오류가 발생하는 지점 > 예외 처리
        isSuccess = kc_user.put_email_verified(user_id)
        if isSuccess == False:
            # 사용자가 회원가입을 동일하게 재진행할 수 있도록 LDAP의 group, user 삭제
            delete_group(user_id)
            delete_user(user_id)
            return False
        
        isSuccess = kc_user.post_user_attributes(user_id, isUser)
        if isSuccess == False:
            delete_group(user_id)
            delete_user(user_id)
            return False           

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

def check_user(user_id):
    search_base = 'ou=users,cn=admin,dc=devstack,dc=co,dc=kr'
    search_filter = "(cn="+user_id+")"

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

def add_group_member(group_name, user_id):
    ldap_conn = connect_ldap_server()

    group_dn = "cn="+str(group_name)+",ou=groups,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        check = check_user(user_id)
        if len(check) == 0:
            return "user"
        check = check_group(group_name)
        if len(check) == 0:
            return "group"

        response = ldap_conn.modify(group_dn, {'memberUid': [(MODIFY_ADD, [user_id])]})
    except LDAPException as e:
        response = e
    return response

def delete_group_member(group_name, user_id):
    ldap_conn = connect_ldap_server()

    group_dn = "cn="+str(group_name)+",ou=groups,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        check = check_user(user_id)
        if len(check) == 0:
            return "user"
        check = check_group(group_name)
        if len(check) == 0:
            return "group"

        response = ldap_conn.modify(group_dn, {'memberUid': [(MODIFY_DELETE, [user_id])]})
    except LDAPException as e:
        response = e
    return response

def delete_group(user_id):
    ldap_conn = connect_ldap_server()
    roles = ['admin', 'editor', 'viewer']
    for role in roles:
        group_name = user_id+"@"+role
        group_dn = "cn="+group_name+",ou=groups,cn=admin,dc=devstack,dc=co,dc=kr"
        try:
            response = ldap_conn.delete(group_dn)
        except LDAPException as e:
           response = e
    return response

def delete_user(user_id):
    ldap_conn = connect_ldap_server()
    user_dn = "cn="+user_id+",ou=users,cn=admin,dc=devstack,dc=co,dc=kr"

    check = check_user(user_id)
    if len(check) == 0:
        return "user"

    delete_group(user_id)
    #ks_project.delete_project(user_name)
    ks_user.delete_user(user_id)

    try:
        response = ldap_conn.delete(user_dn)
    except LDAPException as e:
        response = e
    return response
