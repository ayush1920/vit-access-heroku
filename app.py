from flask import Flask, render_template,request, jsonify
from werkzeug.contrib.fixers import ProxyFix
from flask import send_from_directory
import requests
import urllib3
import sys
from datetime import datetime
import numpy as np
import pytz
import json
import base64
from PIL import Image
from io import BytesIO
global s
s=0

# Initialisation
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
app.config['SECRET_KEY'] ='decf5b3e1ef04cc1185581d3f07c2af0'
user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
vtop_page = "http://vtopcc.vit.ac.in:8080/vtop/"
login_page = "http://vtopcc.vit.ac.in:8080/vtop/vtopLogin"
captcha_page = "http://vtopcc.vit.ac.in:8080/vtop/doRefreshCaptcha"
doLogin_page = "http://vtopcc.vit.ac.in:8080/vtop/doLogin"
attendance_page = "http://vtopcc.vit.ac.in:8080/vtop/processViewStudentAttendance"
routine_page = 'http://vtopcc.vit.ac.in:8080/vtop/processViewTimeTable'
marks_page = "http://vtopcc.vit.ac.in:8080/vtop/examinations/doStudentMarkView"
userAgent ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}


def user_login(regid, password):
    global s
    with requests.session() as s:
        # login changed
        s.get(vtop_page,verify=False,headers= user_agent)
        s.get(login_page,verify=False,headers= user_agent)
        r = s.get(captcha_page,verify=False,headers= user_agent)
        r = r.text
        ind = r.index("src=\"")+5
        ind2 = r.index(" />",ind)-1
        uri = r[ind:ind2]
        encoded_data = uri.split(',')[1]
        img =  np.array(Image.open(BytesIO(base64.b64decode(encoded_data))).convert('L'))
        import captcha
        cap =  captcha.break_captcha(img)
        keys={'uname': regid,'passwd':password,'captchaCheck':cap}
        login =  s.post(doLogin_page,data=keys,verify=False,headers= user_agent)
        return login


@app.route("/attendance", methods = ['POST','GET'])
def getTimeTable(trig=0):
    global s
    val = request.get_json(force=True)
    regid = val["regid"]
    password = val["pass"]
    for i in range(5):
        user_login(regid, password)
        import formatDate
        import parse
        keys={'semesterSubId':"CH2019205",'authorizedID': regid,'x':formatDate.getDate()}
        login = s.post(attendance_page,data=keys,verify=False,headers= user_agent)
        res =  parse.attendanceParse(login.text)
        if res != 'error':
            return res
    return json.dumps({'attendance' : [], "response" : 'Error'})
        

@app.route("/getDate", methods = ['GET','POST'])
def curdate():
    monthlist={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec" }
    date = str(datetime.now(pytz.timezone('Asia/Kolkata'))).split(" ")[0].split("-")[::-1]
    date[1]=monthlist[int(date[1])]
    return "-".join(str(x) for x in date)

@app.route("/routine", methods = ['GET','POST'])
def getRoutine():
    global s
    val = request.get_json(silent=True)
    regid = val["regid"]
    password = val["pass"]

    # iterates for 5 tries
    for i in range(5):
        user_login(regid, password)
        import formatDate
        import parse
        keys={'semesterSubId':"CH2019201",'authorizedID': regid,'x':formatDate.getDate()}
        login = s.post(routine_page,data=keys,verify=False,headers = user_agent)
        res = parse.routineParse(login.text)
        if res != 'error':
            return res
    return json.dumps({'routine' : [], "response" : 'Error'})
    

@app.route("/marks", methods = ['GET','POST'])
def getMarks():
    global s
    val = request.get_json(silent=True)
    regid = val['regid']
    password = val['pass']
    
    # iterates for 5 tries
    for i in range(5):
        user_login(regid, password)
        import formatDate
        import parse
        keys={'semesterSubId':"CH2019201",'authorizedID': regid,'x':formatDate.getDate()}
        login = s.post(marks_page,files={'authorizedID': (None, regid), 'semesterSubId': (None, 'CH2019205')},verify=False,headers= user_agent)
        res = parse.marksParse(login.text)
        if res != 'error':
            return res
    return json.dumps({'marksdata' : [], "response" : 'Error'})

#Logging and running
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
    #app.run(host='0.0.0.0', debug=True, port=80)
