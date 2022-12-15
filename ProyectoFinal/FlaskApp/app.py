from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import json
import bcrypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Univalle'
app.config['MYSQL_DB'] = 'newsDb'

mysql = MySQL(app)

app.secret_key = "mysecretkey"

@app.route('/')
def home():
    return render_template('view_home.html')

##mostrar la lista de registros de la tabla de profesores
@app.route('/list', methods=['GET'])
def users_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user')
    data = cursor.fetchall()
    return render_template('view_register.html', users=data)

#funcion para agregar un nuevo registro a la tabla profesores
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

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=="POST":
       email = request.form['email']
       password = request.form['password'].encode('utf-8')
    
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute('SELECT * FROM user WHERE email=%s',(email))
       user = cursor.fetchone()
       cursor.close()
       if len(user) > 0:
           if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
               session['email'] == user['email']
               session['role'] == user['role']
               session['name'] == user['name']
               return redirect(url_for('users_list')) 
       else:
           return "Error usuario o contrasenha"
    else:
       return redirect(url_for('users_list'))  

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('users_list')) 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
