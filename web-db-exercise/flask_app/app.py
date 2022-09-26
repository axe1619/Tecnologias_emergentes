from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

import MySQLdb.cursors
import json

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'dbcontainer'
app.config['MYSQL_USER'] = 'example_user'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'example'

mysql = MySQL(app)

app.secret_key = "mysecretkey"

##mostrar la lista de registros de la tabla de profesores
@app.route('/', methods=['GET'])
def professor_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM professor')
    data = cursor.fetchall()
    return render_template('view_professor.html', professors=data)

#funcion para agregar un nuevo registro a la tabla profesores
@app.route('/add', methods=['POST'])
def add_professor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        ciudad = request.form['ciudad']
        direccion = request.form['direccion']
        salario = request.form['salario']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO professor (first_name, last_name, city, address, salary) VALUES (%s, %s, %s, %s, %s)',
        (nombre, apellido, ciudad, direccion, salario))
        mysql.connection.commit()
        flash('Nuevo registro agregado')
    return redirect(url_for('professor_list'))

#funcion para eleminar un registro existente
@app.route('/delete/<id>', methods=['POST', 'GET'])
def delete_professor(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM professor WHERE id = %s', (id))
    mysql.connection.commit()
    flash('Registro eliminado')
    return redirect(url_for('professor_list'))

#funcion para llamar a un registro
@app.route('/edit/<id>')
def find_professor(id):

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM professor WHERE id = %s', (id))
    data = cursor.fetchall()
    return render_template('view_professor_edit.html', professor=data[0])

#funcion para modificar datos de un registro existente
@app.route('/update/<id>', methods=['POST'])
def update_professor(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        ciudad = request.form['ciudad']
        direccion = request.form['direccion']
        salario = request.form['salario']
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE professor SET first_name=%s, last_name=%s, city=%s, address=%s, salary=%s WHERE id=%s', (nombre, apellido, ciudad, direccion, salario, id))
        mysql.connection.commit()
        flash('Registro modificado')
    return redirect(url_for('professor_list'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
