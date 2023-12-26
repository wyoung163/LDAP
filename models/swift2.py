import config
from controllers import ks_auth
from swiftclient import ClientException

conn = ks_auth.swift
container = config.CONTAINER
#obj_name = 'local_object.txt'

## container 목록
def get_containers():
    resp_headers, containers = conn.get_account()
    print("Response headers: %s" % resp_headers)
    for container in containers:
        print(container)

## container 생성
# conn.put_container(container)
# resp_headers, containers = conn.get_account()
# if container in containers:
#     print("The container was created")

## object 생성
def post_object(obj):
    with open('local.txt', 'r') as local:
        conn.put_object(
            container,
            obj,
            contents=local,
            content_type='text/plain'
        )

## object 확인
def get_object(obj):
    try:
        resp_headers = conn.head_object(container, obj)
        print('The object was successfully created')
    except ClientException as e:
        if e.http_status == '404':
            print('The object was not found')
        else:
            print('An error occurred checking for the existence of the object')
        
## object 다운로드
def download_object(obj):
    resp_headers, obj_contents = conn.get_object(container, obj)
    with open('local_copy.txt', 'w') as local:
        local.write(obj_contents)

## object 삭제
def delete_object(obj):
    try:
        conn.delete_object(container, obj)
        print("Successfully deleted the object")
    except ClientException as e:
        print("Failed to delete the object with error: %s" % e)   