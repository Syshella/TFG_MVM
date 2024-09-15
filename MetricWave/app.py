import os

from flask import Flask, render_template, request, flash, redirect, url_for

from controllers.results_controller import result_blueprint
from controllers.user_controller import user_blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para los mensajes flash y para las sesiones

# Registrar el Blueprint 'user' para que pueda redirigir a las rutas definidas en user_controller.py
app.register_blueprint(user_blueprint, url_prefix='/')
app.register_blueprint(result_blueprint, url_prefix='/')

@app.route('/')
def index():
    # print(os.listdir('templates'))  # Imprime el contenido de la carpeta templates
    return render_template('index.html')


@app.route('/results')
def results():
    return render_template('results.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/forgot')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/reset/<token>')
def reset_password(token):
    return render_template('reset_password.html')

@app.route('/search')
def search():
    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True, port=9000)
