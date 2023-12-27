# keystone-auth-cli
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from swiftclient import Connection
import config

# Keystone Server 연결
auth = v3.Password(auth_url=config.KS_URL,
        username=config.KS_ADMIN_USERNAME,
        password=config.KS_ADMIN_PASSWORD,
        system_scope="all",
        user_domain_id=config.KS_USER_DOMAIN_ID)
sess = session.Session(auth=auth)
keystone = client.Client(session=sess)

# Swift Client 연결
swift = Connection(session=sess, 
                   preauthurl=config.OS_STORAGE_URL, 
                   preauthtoken=config.OS_AUTH_TOKEN)
