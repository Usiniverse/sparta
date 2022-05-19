from pymongo import MongoClient
import jwt
import datetime
import hashlib
import random
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

##########메일 전송하는 라이브러리(추가)##########################
import smtplib                                        #구글설정->보안->전달 및 POP/IMAP->보안 수준이 낮은 앱의 액세스 활성화!#
from email.mime.text import MIMEText
##########메일 전송하는 라이브러리(추가)##########################


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

################################## 연결 상태 확인하기
client = MongoClient('3.39.190.201', 27017, username="test", password="sparta")
db = client.login

#비밀번호 난수 생성
def genPass():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    password = ""

    for i in range(10):
        index = random.randrange(len(alphabet))
        password = password + alphabet[index]
    return password

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('index.html', payload=payload)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 페이지로
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

#비밀번호 찾기 페이지로
@app.route('/password_find')
def pw():
    msg = request.args.get("msg")
    return render_template('password_find.html', msg=msg)

# 로그인 시
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # 일치하면 로그인 창 오픈
    if result is not None:
        payload = {
        'id': username_receive,
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 불일치하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 비밀번호 찾기
@app.route('/api/password_find', methods=['POST'])
def find():
    id_receive = request.form['id_give']
    email_receive = request.form['email_give']

    #맞는지 확인
    result = db.users.find_one({'username': id_receive, 'email': email_receive})

    #저장된 비밀번호 값 가져옴
    pw = result['password']
    new_pw = genPass()

    #맞으면
    if result is not None:
        password_hash = hashlib.sha256(new_pw.encode('utf-8')).hexdigest()
        db.users.update_one({'password': pw}, {'$set': {'password': password_hash}})


        ######################비밀번호 찾기 시 메일로 전송######################
        sendEmail = 'hanghaeD7.12@gmail.com'    # 나의 이메일
        recvEmail = email_receive               # 상대 이메일
        password = 'gkdgod12!'                  ##############나의 비밀번호###################
        smtpName = "smtp.gmail.com"
        smtpPort = 587
        text = new_pw                          # 내용(새 비밀번호)
        msg = MIMEText(text)
        msg['subject'] = '새 비밀번호 전송.'
        msg['From'] = sendEmail
        msg['To'] = recvEmail
        print(msg.as_string())
        s = smtplib.SMTP(smtpName, smtpPort)        # 메일 서버연결
        s.starttls()                                # TLS 보안처리
        s.login(sendEmail, password)                # 로그인
        s.sendmail(sendEmail, recvEmail, msg.as_string())        # 메일전송, 문자열로 변환
        s.close()                                                # SMTP서버 연결종료
        ######################비밀번호 찾기 시 메일로 전송######################

        return jsonify({'result': 'success', 'pw':new_pw})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입 정보 저장
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    email_receive = request.form['email_give']

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": "",                                          # 프로필 한 마디
        "email": email_receive
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

    # 비밀번호 찾기 페이지로
@app.route('/sign_in')
def logout():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

    #######################################################################
################        메   인  페   이   지  ##########################################
###############################################################################

@app.route('/calories', methods=['POST'])
def post_food():
    food_name_receive = request.form["food_name_give"]
    food_g_receive = request.form["food_g_give"]
    food_kcal_receive = request.form["food_kcal_give"]
    return render_template("calories.html", food_name=food_name_receive, food_g=food_g_receive, food_kcal=food_kcal_receive)


@app.route('/calories/save', methods=['POST'])
def posting():
    today = datetime.now()
    time = today.strftime('%Y-%m-%d-%H-%M')

    filename = f'file-{time}'
    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    food_receive = request.form['food_give']
    total_kcal_receive = request.form['total_kcal_give']

    # token_receive = request.cookies.get('mytoken'),
    # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    # writer = payload['id']

    homework_list = list(db.foods.find({}, {'_id': False}))
    count = len(homework_list) + 1

    food_detail = json.loads(food_receive)

    food_ary = []
    for food in food_detail:
        food_ary.append({
            "food_name": food['food_name'],
            "food_g": food['food_g'],
            "food_kcal": food['food_kcal']
        })



    doc = {
        "food_detail": food_ary,
        "total_kcal": total_kcal_receive,
        "time": today.strftime('%Y.%m.%d'),
        'file': f'{filename}.{extension}',
        'num': count,
        # 'writer': writer
    }
    db.foods.insert_one(doc)

    return jsonify({'msg': '업로드 완료!'})

@app.route('/calories', methods=['GET'])
def show_calories():
    foods = list(db.foods.find({}, {'_id': False}))
    return jsonify({'foods': foods})


#카드 삭제
@app.route("/list/delete", methods=["POST"])
def homework_delete():
    num_receive = request.form['delete_give']
    db.foods.delete_one({'num': int(num_receive)})
    return jsonify({'msg': '삭제 완료!'})

#홈 화면에서 유저 정보 가져오기
@app.route('/get_user', methods=['GET'])
def get_user():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['id']
    return jsonify({'user_id': user_id})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
