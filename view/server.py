from flask import Blueprint, flash, redirect, url_for, render_template, jsonify, request
from os import path, listdir
from werkzeug.utils import secure_filename
import paramiko
from datetime import datetime
from pymongo import MongoClient
import cv2
#-------------------------------------------------------------
from secret.secret import sftp_host, sftp_id, sftp_pw,sftp_port
from secret.secret import mongo_dbaddr,mongo_dbid,mongo_dbport,mongo_dbpw
#-------------------------------------------------------------
server = Blueprint("server",__name__, url_prefix="/server")
#------------------------------------------------------------
client = MongoClient(host=mongo_dbaddr, port=mongo_dbport, username=mongo_dbid, password=mongo_dbpw)
db = client['ds']
col_uf = db['uploaded_file']
col_f4g = db['server_file']
col_s4g = db['schedule4group']
LOCATION = './files/'
#------------------------------------------------------------
d = datetime.today().strftime("%Y-%m-%d")
FILE = '/upload/file/'
QR = '/upload/qr/'
#------------------------------------------------------------
videoFormat = ['mp4', 'avi', 'mkv']
def get_duration(filename):
    for i in videoFormat:
        if i in filename:
            video = cv2.VideoCapture(filename)
            Frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video.get(cv2.CAP_PROP_FPS)
            print(str(Frame_count) +'\n' + str(fps))
            return Frame_count/fps + 1
    return '-'
#------------------------------------------------------------
#sftp 서버 연결 함수
#ssh로 서버 접속하고 sftp를 open하는 방식으로 동작함
#홈 페이지에 들어가면 항상 sftp 서버랑 연결되어있게 함
def serverConnect():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(sftp_host,port=sftp_port,username=sftp_id,password=sftp_pw)
        sftp = ssh.open_sftp()
        print(sftp.listdir())
        return sftp
    except Exception as err:
        print(err)
        return redirect(url_for('server.file_server'))
#sftp 서버 연결
sftp = serverConnect()
#------------------------------------------------------------
@server.route("/")
def server_root():
    return redirect(url_for('server.home'))

#------------------------------------------------------------
#서버 파일 업로드 홈 화면.
#서버가 닫혀있으면 서버를 다시 연결하고 페이지 랜딩
@server.route("/home")
def file_server():
    try:
        return render_template('file_server.html',date = d)
    except Exception as err:
        serverConnect()
        print(err)
        return render_template('file_server.html',date = d)

#------------------------------------------------------------
# 서버에 파일 업로드하기.
# 서버에 존재하는 날짜별 폴더에 맞게 파일 업로드
# 서버에 업로드하면서 동시에 DB업로드 
# 1. 컨텐츠 타입 2. 프로그램 
videoFormat = ['mp4', 'avi', 'mkv']
imgFormat = ['png','jpg']
def VidorImg(str):
    for i in videoFormat:
        if i in str:
            return "video"
    for i in imgFormat:
        if i in str:
            return "img"
    return "-"
def removeFormat(str):
    for i in videoFormat:
        if i in str:
            str.replace("."+i,"")
            return str
    for i in imgFormat:
        if i in str:
            str.replace("."+i,"")
            return str
    return str



@server.route("/server_upload",methods = ['POST'])
def server_upload():
    ret = listdir(LOCATION)
    try:
        file = request.form['file']
        file_Name = file.replace(' ','_')
        if file_Name not in ret:
            flash("파일이 로컬환경에 존재하는 파일인지 확인해주세요")
            return render_template('file_server.html',date=d)
        sftp.chdir(FILE)
        if d not in sftp.listdir():
            sftp.mkdir(d)
            sftp.chdir(QR)
            sftp.mkdir(d)
        sftp.chdir(FILE+d)
        if file_Name in sftp.listdir():
            flash("이미 존재하는 파일입니다.")
            return render_template('file_server.html',date=d)
        #---------------------------------------------------
        inp_type = VidorImg(file_Name)
        inp_direction = request.form['content_type']
        inp_category = request.form['category']
        inp_duration = get_duration(LOCATION+file_Name)
        inp_filepath = FILE + d +"/"+ file_Name
        inp_qrpath = QR + d +"/qr_" +file_Name
        inp_title = removeFormat(file_Name)
        inp_date = datetime.today().strftime("%Y%m%d%H%M%S")
        doc = {
            "type": inp_type,
            "direction": inp_direction,
            "category": inp_category,
            "duration" : inp_duration,
            "title" : inp_title,
            "filepath": inp_filepath,
            "QR": inp_qrpath,
            "date" : inp_date
        }
        print(doc)
        col_f4g.insert_one(doc)
        sftp.put(LOCATION+file_Name, file_Name, callback=None, confirm=True)
        sftp.chdir(QR+d)
        sftp.put(LOCATION+"QR/"+file_Name , file_Name,  callback=None, confirm=True)
        flash("파일 업로드 완료")
        return render_template('file_server.html',date = d)
    except Exception as err:
        flash(err)
        return render_template('file_server.html',date = d)


# 서버에서 파일 삭제하기
# 당일 날짜에 대한 것만 수정가능
@server.route("/server_delete",methods = ['POST'])
def delete():
    try:
        file_Name = request.form['file']
        sftp.chdir(FILE+d)
        if file_Name not in sftp.listdir():
            flash("존재하는 파일인지 확인해주세요")
            return render_template('file_server.html',date = d)
        sftp.remove(FILE+d+'/'+file_Name) 
        return render_template('file_server.html',date = d)
    except Exception as err:
        flash("다시 시도해주세요")
        return render_template('file_server.html',date=d)

#------------------------------------------------------
#서버에 현재 존재하는 파일 목록 가져오기
@server.route("/sFileList_pic",methods = ['POST'])
def sFileList_pic():
    sftp.chdir("/upload/file/"+d)
    ret = sftp.listdir()
    j = {"ret":ret}
    # print(j)
    return jsonify(j)

