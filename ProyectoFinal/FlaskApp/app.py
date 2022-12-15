from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import pickle
import pandas as pd
import MySQLdb.cursors
import bcrypt

app = Flask(__name__)

#configuracion para acceder al servidor y base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Univalle'
app.config['MYSQL_DB'] = 'newsDb'

mysql = MySQL(app)

app.secret_key = "mysecretkey"

#ruta para la vista home
@app.route('/')
def home():
    return render_template('view_home.html')

#ruta para la vista login
@app.route('/login_view')
def login_view():
    return render_template('view_login.html')

#mostrar las lista de registros
@app.route('/list', methods=['GET'])
def users_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user')
    data = cursor.fetchall()
    return render_template('view_register.html', users=data)

#funcion para registrar un nuevo usuario
@app.route('/add', methods=['POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)',
        (name, email, hash_password))
        mysql.connection.commit()
        flash('Su cuenta ha sido creado con exito', "info")
        session['name'] = name
        session['email'] = email
    return redirect(url_for('users_list'))

#eliminar registro existente de la tabla usuario
@app.route('/delete/<id>', methods=['POST', 'GET'])
def delete_user(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM user WHERE id_user = %s', (id))
    mysql.connection.commit()
    flash('Registro eliminado')
    return redirect(url_for('users_list'))

#funcion para iniciar sesion
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=="POST":
       email = request.form['email']
       password = request.form['password'].encode('utf-8')
    
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute('SELECT * FROM user WHERE email=%s',(email,))
       user = cursor.fetchone()
       cursor.close()
       if len(user) > 0:
           if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
               session['email'] = user['email']
               session['role'] = user['role']
               session['name'] = user['name']
               return redirect(url_for('home')) 
       else:
           flash('Email o contrasenha incorrecto', "info")
           return "Error usuario o contrasenha"
    else:
       return redirect(url_for('users_list'))  

#funcion para cerrar sesion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home')) 


#uso de machine learning en python
tfvect = TfidfVectorizer(stop_words='english', max_df=0.7)

#cargar el modelo para el dataset
loaded_model = pickle.load(open('model.pkl', 'rb'))

#datset usados para el entrenamiento de la app
true = pd.read_csv('True.csv')
fake = pd.read_csv('Fake.csv')
data = pd.read_csv('news.csv')

#etiquetar las noticias
true['target'] = 'true'
fake['target'] = 'fake'

x = data['text']
y = data['label']

#variables para entrenar el dataset
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

#funcion para concatenar dos archivos
def concat_file(file_true, file_fake):
    #concatenar los archivos true y fake en un solo dataset
    dataset = pd.concat([file_true, file_fake]).reset_index(drop = True)
    dataset['text'] = dataset['text'].apply(lambda x: x.lower())
    return dataset

#funcion para ordenacion y shuffle
def shuffling_file(dataset):
    data = shuffle(dataset)
    data = data.reset_index(drop=True)
    return data

#funcion para limipar datos del dataset
def clear_file(dataset):
    clear_data = dataset.drop(["date"],axis=1,inplace=True)
    clear_data = dataset.drop(["title"],axis=1,inplace=True)
    return clear_data

#funcion para detectar la noticia usando prediccion
def detect_news(news):
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    input_data = [news]
    vectorized_input_data = tfvect.transform(input_data)
    prediction = loaded_model.predict(vectorized_input_data)
    print(tfid_x_test)
    print(tfid_x_train)
    return prediction

#ruta para la vista de deteccion de noticias
@app.route('/detector')
def detector_view():
    return render_template('view_detector.html')

#funcion para enviar la deteccion de la noticia ingresada
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        pred = detect_news(message)
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO news (text, target) VALUES (%s, %s)',
        (message, pred))
        mysql.connection.commit()
        flash(pred, "info")
        return render_template('view_detector.html', prediction=pred)
    else:
        flash("Vuelve a intentar mas tarde!", "info")
        return render_template('view_detector.html', prediction="Esta en proceso!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
