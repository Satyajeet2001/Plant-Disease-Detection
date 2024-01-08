from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import tensorflow as tf
import numpy as np
import cv2
import os
import datetime

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'plant'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'plant'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/')
def index():
    msg = request.args.get('msg')
    if msg:
        return render_template('index.html', msg=msg)
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form and 'mobile' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO users VALUES (NULL,%s, %s, %s, %s)', (name, email, password, mobile))
        mysql.connection.commit()
        msg = 'You have been registered successfully!'
        return redirect(url_for('index', msg=msg))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        data = cursor.fetchone()
        if data:
            session['email'] = email
            session['id'] = data['id']
            session['loggedin'] = True
            return redirect(url_for('dashboard'))
        else:
            msg = 'Invalid login details. Please type valid input details.'
            return redirect(url_for('index',msg=msg))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id',None)
    session.pop('email',None)
    session.pop('loggedin',None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if session['loggedin']:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))

def predict_class(path):
    img = cv2.imread(path)

    RGBImg = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    RGBImg= cv2.resize(RGBImg,(224,224))
    image = np.array(RGBImg) / 255.0
    new_model = tf.keras.models.load_model("64x3-CNN.model")
    predict=new_model.predict(np.array([image]))
    per=np.argmax(predict,axis=1)
    if per == 0:
        return 'Pepper Bell Bacterial Spot Disease', 0
    if per == 1:
        return 'Pepper Bell Healthy', 1
    if per == 2:
        return 'Potato Early Blight Disease', 2
    if per == 3:
        return 'Potato Healthy', 3
    if per == 4:
        return 'Potato Late Blight Disease', 4
    if per == 5:
        return 'Tomato Target Spot Disease', 5
    if per == 6:
        return 'Tomato Mosaic Virus Disease', 6
    if per == 7:
        return 'Tomato Yellow Leaf Curl Virus Disease', 7
    if per == 8:
        return 'Tomato Bacterial Spot Disease', 8
    if per == 9:
        return 'Tomato Early Blight Disease', 9
    if per == 10:
        return 'Tomato healthy', 10
    if per == 11:
        return 'Tomato Late Blight Disease', 11
    if per == 12:
        return 'Tomato Leaf Mold Disease', 12
    if per == 13:
        return 'Tomato Septoria Leaf Spot Disease', 13
    if per == 14:
        return 'Tomato Spotted Spider Mite Disease', 14
    
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload', methods=['GET','POST'])
def upload():
    if session['loggedin']:
        if request.method == 'POST':
            f = request.files['file']
            if f and '.' in f.filename and f.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                file_ext = f.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
                f.save(file_path)
                predict, classtype = predict_class(file_path)
                current_datetime = datetime.datetime.now()
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO user_history VALUES (NULL,%s, %s, %s, %s)', (session['id'], file_path, predict, current_datetime))
                mysql.connection.commit()
                if classtype != 1 or classtype !=  3 or classtype != 10:
                    return render_template('upload-file.html', file_path=file_path, file_result=predict, pestshow=1)
                return render_template('upload-file.html', file_path=file_path, file_result=predict)
        return render_template('upload-file.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/history', methods=['GET','POST'])
def history():
    if session['loggedin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user_history WHERE user_id = %s", (session['id'],))
        all_data = cursor.fetchall()
        return render_template('view-history.html',all_data=all_data)
    else:
        return redirect(url_for('index'))
    
@app.route('/pestcontrol', methods=['GET','POST'])
def pestcontrol():
    return render_template('pest-control.html')
    
def get_image_address(image_path):
    image_path = image_path.replace("\\", "/")
    return image_path
app.jinja_env.globals.update(get_image_address=get_image_address)
