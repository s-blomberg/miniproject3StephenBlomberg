# INF601 - Programming in Python
# Stephen Blomberg
# Mini Project 3

from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('collection', __name__)

#view for index, accesses the db, fetches all albums, puts into list and loops.
@bp.route('/')
@login_required
def index():
    db = get_db()
    collection = db.execute(
        'SELECT a.id, title, artist, release_year, variant'
        ' FROM collection a JOIN user u ON a.user_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY title',
        (g.user['id'],)
    ).fetchall()
    return render_template('collection/index.html', collection=collection)

#view for adding a new album
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        release_year = request.form['release_year']
        variant = request.form['variant']
        error = None

        if not title:
            error = 'Title is required.'
        elif not artist:
            error = 'Artist is required.'
        elif error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO collection (title, artist, release_year, variant, user_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, artist, release_year, variant, g.user['id'])
            )
            db.commit()
            return redirect(url_for('collection.index'))

    return render_template('collection/create.html')


#function to retrieve album from db, verify auth, update album by session id
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    album = get_album(id)

    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        release_year = request.form['release_year']
        variant = request.form['variant']
        error = None

        if not title:
            error = 'Title is required.'
        elif not artist:
            error = 'Artist is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE collection SET title = ?, artist = ?, release_year = ?, variant = ?'
                ' WHERE id = ?',
                (title, artist, release_year, variant, id)
            )
            db.commit()
            return redirect(url_for('collection.index'))

    return render_template('collection/update.html', album=album)



#function to retrieve album from db and view by id
def get_album(id, check_user=True):
    album = get_db().execute(
        'SELECT * FROM collection WHERE id = ?', (id,)
    ).fetchone()

    if album is None:
        abort(404, f"Album id {id} doesn't exist.")

    if check_user and album['user_id'] != g.user['id']:
        abort(403)

    return album

@bp.route('/collection/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_album(id)
    db = get_db()
    db.execute('DELETE FROM collection WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('collection.index'))



