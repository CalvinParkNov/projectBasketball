from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime

from pymongo import MongoClient
import hashlib


app = Flask(__name__)
client = MongoClient(
    'mongodb+srv://calvinpark:SUh0Rg03cwGTCjon@nodeexpressprojects.p7rnvju.mongodb.net/?retryWrites=true&w=majority')
db = client.basketball
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    basketball_list = list(db.basketball.find({}, {'_id': False}))
    return render_template('index.html', list=basketball_list)



@app.route('/createAccount')
def acoount():
    return render_template('member/createAccount.html')


@app.route('/api/register', methods=['POST'])
def create_account():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


@app.route('/login')
def login():
    return render_template('member/login.html')


@app.route('/api/login', methods=['POST'])
def loginUser():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/write')
def write():
    token_receive = request.cookies.get('mytoken')
    if not token_receive:
        flash("로그인 정보가 존재하지 않습니다.")
        return redirect(url_for("login"))
    return render_template('content/write.html')


@app.route('/submitContent', methods=['POST'])
def submit():
    location = request.form['location']
    title = request.form['title']
    content = request.form['content']
    players = request.form['players']
    play_type = request.form['type']
    address = request.form['address']
    count = len(list(db.basketball.find({}, {'_id': False})))

    doc = {
        'index': count + 1,
        'title': title,
        'location': location,
        'players': players,
        'content': content,
        'play_type': play_type,
        'address': address,
        'ins_date': datetime.today().strftime('%Y-%m-%d')
    }

    db.basketball.insert_one(doc)
    flash("등록되었습니다.")
    return redirect(url_for('home'))


@app.route('/attend', methods=['POST'])
def attend():
    print(request.form['index'])


if __name__ == '__main__':
    app.run('0.0.0.0', port=4000, debug=True)
