from flask import Flask, request
app = Flask(__name__)

#import sys, os
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from controllers import signup

@app.route('/signup', methods=['POST'])
def signUp():
    req = request.json
    user_name = req['user_name']
    user_sn = req['user_sn']
    user_gname = req['user_gname']
    user_mail = req['user_mail']
    user_passwd = req['user_passwd']
    
    res = signup.add_user(user_name=user_name, user_sn=user_sn, user_gname=user_gname, user_mail=user_mail, user_passwd=user_passwd)
    if res == True:
        return "success"
    else:
        return "fail"

if __name__ == '__main__':
    app.run(port='3000')