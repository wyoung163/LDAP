from flask import Flask, request, Response, json, Blueprint
from flask_restx import Api, Resource, fields
#from flask_restplus import reqparse
from werkzeug.utils import secure_filename
from controllers import signup, ks_project, ldap
import os

# file 임시 저장소 (테스트용)
bp = Blueprint('image', __name__, url_prefix='/company/auth')

app = Flask(__name__)
api = Api(app, version='1.0', title='인증 API', description='Swagger', doc="/api-docs")
auth_api = api.namespace('', description='SignUp API')

class _Schema():
    post_fields = auth_api.model("회원 가입 시 필요한 데이터", {
        # 'username': fields.String(description="사용자 아이디", example="cwy"),
        # 'last_name': fields.String(description="사용자 성", example="choi"),
        # 'given_name': fields.String(description="사용자 이름", example="wyoung"),
        # 'email': fields.String(description="사용자 이메일", example="cwy@test.com"),
        # 'password': fields.String(description="사용자 비밀번호", example="1234"),
    })

@auth_api.route('/auth')
@auth_api.expect(_Schema.post_fields)
class signUp(Resource):
    def post(self):
        req = request.form
        user_id = req['id']
        user_name = req['username']
        mail = req['email']
        passwd = req['password']
        phone = req['phone']
        address = req['address']

        res = ldap.add_user(user_id, user_name, mail, passwd, True)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error": { "code": 409, "title": "Duplicated user" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        elif res == "mail":
            body = '{ "Error": { "code": 409, "title": "Duplicated email" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        elif res == 409:
            body = '{ "Error": { "code": 409, "title": "Duplicated project" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")
        
    def delete(self):
        req = request.args
        name =  req.get('user')

        ks_project.delete_project(name)
        res = ldap.delete_user(name)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404.  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")

@auth_api.route('/company/auth')
@auth_api.expect(_Schema.post_fields)
class signUp(Resource):
    def post(self):
        req = request.form
        id = req["id"]
        company = req['company']
        mail = req['email']
        passwd = req['password']
        name = req['name']
        phone = req['phone']
        address = req['address']
        registration_num = req['registration_num']

        # 사업자 등록증 (파일)
        file = request.files['file']
        file.save('./company1.' + secure_filename(file.filename))

        res = ldap.add_user(id, company, mail, passwd, True)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error": { "code": 409, "title": "Duplicated user" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        elif res == "mail":
            body = '{ "Error": { "code": 409, "title": "Duplicated email" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        elif res == 409:
            body = '{ "Error": { "code": 409, "title": "Duplicated project" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")

@auth_api.route('/admin/auth')
@auth_api.expect(_Schema.post_fields)
class adminSignUp(Resource):
    def post(self):
        req = request.form
        name = req['username']
        mail = req['email']
        passwd = req['password']

        res = ldap.add_user(user_name=name, user_sn=name, user_gname=name, user_mail=mail, user_passwd=passwd, isUser=False)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error": { "code": 409, "title": "Duplicated user" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        elif res == "mail":
            body = '{ "Error": { "code": 409, "title": "Duplicated email" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        elif res == 409:
            body = '{ "Error": { "code": 409, "title": "Duplicated project" } }'
            return Response(response=json.dumps(body), status=409, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")
        
@auth_api.route('/group')
@auth_api.expect(_Schema.post_fields)
class group(Resource):
    def patch(self):
        req = request.args
        group_name = req.get('group')
        user_name = req.get('user')

        res = ldap.add_group_member(group_name = group_name, user_id=user_name)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404.  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        elif res == "group":
            body = '{ "Error" : { "code": 404.  "title": "Group not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")
        
    def delete(self):
        req = request.args
        group_name = req.get('group')
        user_name = req.get('user')

        res = ldap.delete_group_member(group_name = group_name, user_id=user_name)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404.  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        elif res == "group":
            body = '{ "Error" : { "code": 404.  "title": "Group not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")

@auth_api.route('/projectId')
class addProjectId(Resource):
    def post(self):
        req = request.args
        project_name = req.get('name')

        res = ks_project.post_project_id(project_name)

        if int(str(res)[11:14]) <= 204:
            return "{ Success: true }"
        else:
            return "{ Success: False }"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='3000')
