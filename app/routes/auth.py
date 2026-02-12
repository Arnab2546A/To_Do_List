from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_cursor

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=["GET", "POST"]) 
def login():
    if 'user_id' in session:
        return redirect(url_for('tasks.view_tasks'))

    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required', 'danger')
        else:
            with get_cursor() as (cur, _):
                cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
            if row and check_password_hash(row[2], password):
                session['user_id'] = row[0]
                session['user'] = row[1]
                flash('Login Successful', 'success')
                return redirect(url_for('tasks.view_tasks'))
            else:
                flash('Invalid username or password', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=["GET", "POST"]) 
def register():
    if 'user_id' in session:
        return redirect(url_for('tasks.view_tasks'))

    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            flash('Username and password are required', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            with get_cursor() as (cur, _):
                cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
                exists = cur.fetchone()
                if exists:
                    flash('Username already taken', 'danger')
                else:
                    cur.execute(
                        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                        (username, generate_password_hash(password))
                    )
                    flash('Registration successful. Please log in.', 'success')
                    return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    flash('Logged Out', 'info')
    return redirect(url_for('auth.login'))