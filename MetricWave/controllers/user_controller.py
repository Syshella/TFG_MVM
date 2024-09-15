from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy.testing.pickleable import User
from werkzeug.security import generate_password_hash

user_blueprint = Blueprint('user', __name__)
API_URL = "http://127.0.0.1:9100/users"

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Hacer la solicitud POST al backend
        try:
            response = requests.post(f'{API_URL}/login', json={'email': email, 'password': password})
            if response.status_code == 200:
                session['user'] = email
                session['logged_in'] = True
                # flash('Login successful', 'success')
                return redirect(url_for('index'))  # Redirige a la página principal
            else:
                flash('Invalid credentials, please try again.', 'danger')
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}", 'danger')

    return render_template('login.html')


@user_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = requests.post(f'{API_URL}/register', json={'email': email, 'name': email, 'password': password})
            if response.status_code == 201:
                flash('User registered successfully', 'success')
                return redirect(url_for('login'))
            else:
                flash('An error occurred, please try again', 'danger')
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}", 'danger')
    return render_template('login.html')


@user_blueprint.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            response = requests.post(f'{API_URL}/forgot_password', json={'email': email, 'name': email})
            # No informa si el email existe o no para evitar ataques de fuerza bruta
            flash('If your email exists whithin our database, you will receive an email shortly', 'info')
            return redirect(url_for('user.login'))
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}", 'danger')
    return render_template('forgot_password.html')



@user_blueprint.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        return render_template('reset_password.html', token=token)
    if request.method == 'POST':
        password = request.form['password']
        try:
            response = requests.post(f'{API_URL}/reset_password/{token}', json={'password': password})
            if response.status_code == 200:
                flash('Password reset successfully', 'success')
                return redirect(url_for('user.login'))
            else:
                flash('An error occurred, please try again', 'danger')
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}", 'danger')
    return render_template('reset_password.html')
