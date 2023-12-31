from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException, LDAPBindError
from controllers import kc_user, kc_group, kc_client
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

def add_group(user_name):
    ldap_attr = {}
    ldap_attr['objectClass'] = ['top', 'posixGroup']
    new_gid = config.LDAP_NEW_GID

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
        time.sleep(1)
        kc_client.post_admin_access_token()
        kc_group.get_group(user_id=user_name)


    except LDAPException as e:
        response = (" The error is ", e)

    ldap_conn.unbind()
    print(response)
    return response

def add_user(user_name, user_sn, user_gname, user_mail, user_passwd):
    ldap_attr = {}
    ldap_attr['cn'] = user_name 
    ldap_attr['sn'] = user_sn 
    ldap_attr['givenName'] = user_gname
    ldap_attr['mail'] = user_mail
    #ldap_attr['userPassword'] = os.getenv('LDAP_NEW_USER_PASSWD')

    ldap_conn = connect_ldap_server()
    
    user_dn = "cn="+str(user_name)+",ou=users,cn=admin,dc=devstack,dc=co,dc=kr"
    try:
        response = ldap_conn.add(dn=user_dn,
                                object_class='inetOrgPerson',
                                attributes=ldap_attr)
        time.sleep(1)
        add_group(user_name)
        
        #kc_user.get_user_id(user_name=user_name)
        #kc_user.put_user_password(user_passwd=user_passwd)
        kc_user.put_email_verified(user_id=user_name)

    except LDAPException as e:
        response = e
    return response