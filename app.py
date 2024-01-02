from flask import Flask, request, Response, json, Blueprint
from flask_restx import Api, Resource, fields
#from flask_restplus import reqparse
from werkzeug.utils import secure_filename
from controllers import signup, ks_project, ldap
from models import swift
import os

# file 임시 저장소 (테스트용)
#bp = Blueprint('image', __name__, url_prefix='/company/auth')

app = Flask(__name__)
api = Api(app, version='1.0', title='인증 API', description='Swagger', doc="/api-docs")
auth_api = api.namespace('auth', description='회원가입/탈퇴 API')
user_api = api.add_namespace('user', description="회원 정보 관련 API")
group_api = api.namespace('group', description='사용자 초대 API')

class _Schema():
    post_fields = auth_api.model("[개인 회원] 회원 가입 시 필요한 데이터", {
        'id': fields.String(description="아이디", example="cwy"),
        'username': fields.String(description="사용자 이름", example="최누구"),
        'email': fields.String(description="이메일", example="cwy@test.com"),
        'password': fields.String(description="비밀번호", example="1234"),
        'phone': fields.String(description="전화번호", example="010-0000-0000"),
        'address': fields.String(description="주소", example="서울특별시 성북구 화랑도 11길 26"),
    })

    post_fields_2 = auth_api.model("[기업 회원] 회원 가입 시 필요한 데이터", {
        'id': fields.String(description="아이디", example="company01"),
        'name': fields.String(description="담당자 이름", example="최누구"),
        'company': fields.String(description="회사 이름", example="company01"),
        'email': fields.String(description="이메일", example="test@company.co.kr"),
        'password': fields.String(description="비밀번호", example="4321"),
        'phone': fields.String(description="전화번호", example="02-0000-0000"),
        'address': fields.String(description="주소", example="서울특별시 성북구 화랑도 11길 26"),
        'registration_num': fields.String(description="사업자 등록 번호", example="114-54-235642"),
        'file': fields.String(description="사업자 등록증", example="사업자등록증.pdf"),
    })

    delete_fields = auth_api.model("회원 가입 시 필요한 데이터", {
        'user': fields.String(description="아이디", example="cwy"),
    })


@auth_api.route('/')
@auth_api.expect(_Schema.post_fields)
class signUp(Resource):
    ## 개인 회원 회원가입
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
        
    # 회원 탈퇴
    def delete(self):
        req = request.form
        id =  req['id']
        #password = req['password']

        res = ldap.delete_user(id)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404,  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        elif res == "passwd":
            body = '{ "Error" : { "code": 401,  "title": "Incorrect password" } }'
            return Response(response=json.dumps(body), status=401, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")

@auth_api.route('/business')
@auth_api.expect(_Schema.post_fields_2)
class signUp(Resource):
    ## 기업 회원 회원가입
    def post(self):
        req = request.form
        id = req["id"]
        company = req['company']
        mail = req['email']
        passwd = req['password']
        #manager = req['manager']
        phone = req['phone']
        address = req['address']
        registration_num = req['registration_num']

        # 사업자 등록증 (pdf) 
        file = request.files['file']
        #file.save('./data/' + company + '.pdf')
        #res = swift.post_object(str(company+'.pdf'))

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

# @auth_api.route('/admin')
# @auth_api.expect(_Schema.post_fields)
# class adminSignUp(Resource):
#     def post(self):
#         req = request.form
#         name = req['username']
#         mail = req['email']
#         passwd = req['password']

#         res = ldap.add_user(user_id=name, user_name=name, user_gname=name, user_mail=mail, user_passwd=passwd, isUser=False)
#         if res == True:
#             body = '{ "Success": true }'
#             return Response(response=json.dumps(body), status=200, mimetype="application/json")
#         elif res == "user":
#             body = '{ "Error": { "code": 409, "title": "Duplicated user" } }'
#             return Response(response=json.dumps(body), status=409, mimetype="application/json")
#         elif res == "mail":
#             body = '{ "Error": { "code": 409, "title": "Duplicated email" } }'
#             return Response(response=json.dumps(body), status=409, mimetype="application/json")
#         elif res == 409:
#             body = '{ "Error": { "code": 409, "title": "Duplicated project" } }'
#             return Response(response=json.dumps(body), status=409, mimetype="application/json")
#         else:
#             body = '{ "Success": false }'
#             return Response(response=json.dumps(body), status=500, mimetype="application/json")
        
# 개인 회원 정보 변경
@user_api.route('/')
#@user_api.expect(_Schema.post_fields)
class group(Resource):
    def patch(self):
        req = request.form
        id =  req['id']
        user_name = req['username']
        mail = req['email']
        phone = req['phone']
        address = req['address']

        res = ldap.modify_user(id, user_name, mail)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404.  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")
        
# 기업 회원 정보 변경
@user_api.route('/business')
#@user_api.expect(_Schema.post_fields)
class group(Resource):
    def patch(self):
        req = request.form
        id = req['id']
        company = req['company']
        mail = req['email']
        #manager = req['manager']
        phone = req['phone']
        address = req['address']
        registration_num = req['registration_num']

        res = ldap.modify_business_user(id, company, mail)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404.  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")

# 비밀번호 변경
@user_api.route('/password')
#@user_api.expect(_Schema.post_fields)
class group(Resource):
    def patch(self):
        req = request.form
        user_id = req.get('id')
        password = req.get('password')

        res = ldap.modify_password(user_id, password)
        if res == True:
            body = '{ "Success": true }'
            return Response(response=json.dumps(body), status=200, mimetype="application/json")
        elif res == "user":
            body = '{ "Error" : { "code": 404.  "title": "User not found" } }'
            return Response(response=json.dumps(body), status=404, mimetype="application/json")
        else:
            body = '{ "Success": false }'
            return Response(response=json.dumps(body), status=500, mimetype="application/json")      

@group_api.route('/')
@group_api.expect(_Schema.post_fields)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='3000')
