# INF601 - Programming in Python
# Stephen Blomberg
# Mini Project 3

import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

#/auth
bp = Blueprint('auth', __name__, url_prefix='/auth')


#/auth/register
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')



#/auth/login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        #creates session cookie for id auth later
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('collection.index'))

        flash(error)

    return render_template('auth/login.html')



#/auth/logout
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))



#checks session cookie for user id
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()



#checks if user is authenticated before action
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        #if no session cookie id, redirect to login page
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


