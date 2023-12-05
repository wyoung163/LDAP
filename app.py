from flask import Flask, request
from flask_restx import Api, Resource, reqparse, fields
app = Flask(__name__)
api = Api(app, version='1.0', title='인증 API', description='Swagger', doc="/api-docs")
auth_api = api.namespace('', description='SignUp API')
from controllers import signup

class _Schema():
    post_fields = auth_api.model("회원 가입 시 필요한 데이터", {
        'username': fields.String(description="사용자 아이디", example="cwy"),
        'last_name': fields.String(description="사용자 성", example="choi"),
        'given_name': fields.String(description="사용자 이름", example="wyoung"),
        'email': fields.String(description="사용자 이메일", example="cwy@test.com"),
        'password': fields.String(description="사용자 비밀번호", example="1234"),
    })

@auth_api.route('/signup')
@auth_api.expect(_Schema.post_fields)
class signUp(Resource):
    def post(self):
        req = request.json
        user_name = req['username']
        user_sn = req['last_name']
        user_gname = req['given_name']
        user_mail = req['email']
        user_passwd = req['password']
        
        res = signup.add_user(user_name=user_name, user_sn=user_sn, user_gname=user_gname, user_mail=user_mail, user_passwd=user_passwd)
        if res == True:
            return "{ Success: true }"
        else:
            return "{ Success: False }"

if __name__ == '__main__':
    app.run(port='3000')
