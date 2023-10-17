import requests
from urllib.parse import urlencode
from http.client import HTTPConnection
from flask import Flask, redirect, render_template, request, url_for, session
import sqlite3
import oauthlib
from oauthlib import oauth2
import os
from tools import *
from collections import defaultdict
from should_not_share import client_id_r

# from SearchFiles import m
app = Flask(__name__, static_folder="templates")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"  # 允许使用HTTP进行OAuth, 方便本地测试


colleges = {"010":"船舶", "020":"机动", "030":"电院", "070":"理学", "080": "生科", "090":"人文", 
           "110":"化学", "120":"安泰", "130":"国际事务", "140":"外国语", "150":"农生", 
           "160":"环境", "170":"药学", "190":"法学", "200":"媒体", "210":"微电子",
           "220":"网络教育", "251":"体育", "370":"密西根", "413":"空天", "700":"医学"}

colleges = defaultdict(str, colleges)

kw = {
    "response_type": "code",
    "scope": "openid",
    "client_id": "s6BhdRkqt3",
    "redirect_uri": "127.0.0.1:8081/"
}

# @app.route('/', methods=['POST', 'GET'])
# def bio_data_form():
#     if request.method == "POST":
#         username = request.form['username']
#         # age = request.form['age']
#         email = request.form['email']
#         hobbies = request.form['hobbies']
#         return redirect(url_for('showbio', username=username, email=username, hobbies=hobbies))
#     return render_template("in.html")


# @app.route('/showbio', methods=['GET'])
# def showbio():
#     username = request.args.get('username')
#     age = request.args.get('age')
#     email = request.args.get('email')
#     hobbies = request.args.get('hobbies')
#     return render_template("show_bio.html", username=username, age=age, email=email, hobbies=hobbies)


OAUTH = {	# 配置参数，如果没有设置正确，OAuth流程就会失败
    "client_id": client_id_r, # 未申请到, 目前不可用
    "client_secret": "ab94b30cb1sd65885c9f05evf8b1a47c8de0ef96b2e1b2b5028a192e05g65e38",
    "redirect_uri": "http://192.168.0.1/login/oauth/callback/",
    "scope": "openid",
    "auth_url": "https://jaccount.sjtu.edu.cn/oauth2/authorize",
    "token_url": "http://gitlab.test/oauth/token",
    "api_url": "https://api.sjtu.edu.cn/v1/me/profile",
}


@app.route("/login/oauth/", methods=["GET"])
def oauth():
    """ 当用户点击该链接时, 把用户重定向到OAuth2登录页面。 """
    client = oauth2.WebApplicationClient(OAUTH["client_id"])
    state = client.state_generator()    # 生成随机的state参数，用于防止CSRF攻击
    auth_url = client.prepare_request_uri(OAUTH["auth_url"],
                                          OAUTH["redirect_uri"],
                                          OAUTH["scope"],
                                          state)  # 构造完整的auth_url，接下来要让用户重定向到它
    # session["oauth_state"] = state
    return redirect(auth_url)


@app.route("/login/oauth/callback/", methods=["GET"])
def oauth_callback():
    """ 服务器在同意授权之后, 会被重定向回到这个URL。 """
    # 解析得到code
    # client = oauth2.WebApplicationClient(OAUTH["client_id"])
    # code = client.parse_request_uri_response(request.url, session["oauth_state"]).get("code")

    # # 请求获取token
    # body = client.prepare_request_body(grant_type="authorization_code",
    #                                    code=code,
    #                                    redirect_uri=OAUTH["redirect_uri"],
    #                                    client_secret=OAUTH["client_secret"])
    # r = requests.post(OAUTH["token_url"], body)
    # access_token = r.json().get("access_token")
    # id_token = r.json().get("id_token")
    id_token = '''eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJzNkJoZFJrcXQzIiwiaXNzIjoiaHR0cHM6Ly9\
    qYWNjb3VudC5kZXYuc2p0dS5lZHUuY24vb2F1dGgyLyIsInN1YiI6InRlc3QtdXNlciIsImV4cCI6MTMxMTI4MTk3MCwiaWF0Ijo\
    xMzExMjgwOTcwLCJuYW1lIjoi5byg5LiJIiwiY29kZSI6IjEyMzQ1NiIsInR5cGUiOiJzdHVkZW50In0.J6ZZ03Kzqy4-7UKlSYr\
    uZkLMQMVLpfZehU0DM6gmylk''' # 由于目前不能使用oauth2, 先使用这个用于测试
    
    id_info = getinfo(id_token)
    # print(type(id_info))
    session["name"] = id_info["name"]
    session["type"] = id_info["type"]
    session["code"] = id_info["code"]

    # 查询用户名并储存
    # api_path = "/user"
    # url = OAUTH["api_url"] + "?" + \
    #     urlencode({"access_token": access_token})
    # r = requests.get(url)
    # data = r.json()
    # session["username"] = data.get("username")
    # session["access_token"] = access_token  # 以后存到用户表中

    return redirect(url_for(".home"))


@app.route("/logout/", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect("/")

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        purpose = request.form["purpose"]
        college = request.form["college"]
        if not college:
            college = colleges[session["code"]]
        clet = moni_client(session['name'], id=session["code"][3:6], purpose=purpose)
        add_db(clet)
        return render_template("show_bio.html") # 此处应为登记成功页面
    
    return render_template("show_bio.html", username=session["name"], email=session["code"], hobbies=session['type'])


# @app.route("/", methods=["GET"])
# def home():
#     username = session.get("username")
#     if username:
#         context = {"title": "主页", "msg": "你已登录：{}".format(username),
#                    "url": "/logout/", "url_name": "登出"}
#         return render_template("common.html", **context)
#     else:
#         context = {"title": "主页", "msg": "你还没有登录。",
#                    "url": "/login/oauth/", "url_name": "通过Gitlab登录"}
#         return render_template("common.html", **context)





if __name__ == '__main__':
    app.secret_key = "super super secret key" # just for debuging, os.urandom(24)
    # app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, port=8081)
