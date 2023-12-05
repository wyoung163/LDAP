import requests
import xml.etree.ElementTree as elemTree
tree = elemTree.parse('../keys.xml')

url = tree.find('string[@name="OS_AUTH_URL"]').text
unscoppend_token = ""



def get_token():
    idp = tree.find('string[@name="OS_IDP"]').text
    protocol = tree.find('string[@name="OS_PROTOCOL"]').text
    res = requests.get(url+"/v3/OS-FEDERATION/identity_providers/"+idp+"/protocols/"+protocol+"/auth",
                       verify=False)

    global unscoppend_token
    unscoppend_token = res.headers.get("X-Subject-Token")

def get_project_id(project_name):
    params = {
    "name": project_name
    }

    res = requests.get(url+"/v3/projects",
                       params=params,
                       verify=False)
    global client_id
    client_id = res.json()[0].get("id")
    