from flask import Blueprint, session, redirect, url_for, render_template, jsonify, request
from werkzeug.utils import secure_filename
from os import remove, path
import paramiko
from pymongo import MongoClient
#-------------------------------------------------------------
from secret.secret import sftp_host, sftp_id, sftp_pw,sftp_port
from secret.secret import mongo_dbaddr,mongo_dbid,mongo_dbport,mongo_dbpw
#-------------------------------------------------------------
server = Blueprint("server",__name__, url_prefix="/server")
#------------------------------------------------------------
client = MongoClient(host=mongo_dbaddr, port=mongo_dbport, username=mongo_dbid, password=mongo_dbpw)
db = client['ds']
col_uf = db['uploaded_file']
col_f4g = db['file4group']
col_s4g = db['schedule4group']
LOCATION = './files/'
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
#sftp를 전역으로 선언하기
sftp = serverConnect()
#------------------------------------------------------------

@server.route("/")
def server_root():
    return redirect(url_for('server.home'))

#서버 파일 업로드 홈 화면.
#서버가 닫혀있으면 서버를 다시 연결하고 페이지 랜딩
@server.route("/home")
def file_server():
    try: 
        return render_template('file_server.html')
    except Exception as err:
        serverConnect()
        return render_template('file_server.html')

#------------------------------------------------------------
# 서버에 파일 업로드하기.
# 사진인지 영상인지 구분해서 업로드* 중요
# 업로드 정보는 DB에서 찾아서 올리기
@server.route("/server_upload",methods = ['POST'])
def server_upload():
    return redirect(url_for('server.file_server'))


#서버에서 파일 삭제하기
@server.route("/server_delete")
def delete():
    return render_template('file_server.html')

#------------------------------------------------------
#서버에 현재 존재하는 사진파일 목록 가져오기
@server.route("/sFileList_pic",methods = ['POST'])
def sFileList_pic():
    sftp.chdir("/upload/img")
    ret = sftp.listdir()
    j = {"ret":ret}
    print(j)
    return jsonify(j)

#서버에 존재하는 영상파일 목록
@server.route("/sFileList_video",methods = ['POST'])
def sFileList_video():
    sftp.chdir("/upload/video")
    ret = sftp.listdir()
    j = {"ret":ret}
    print(j)
    return jsonify(j)


