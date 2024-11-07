# INF601 - Programming in Python
# Stephen Blomberg
# Mini Project 3

import os
from flask import Flask


# create and configure the app factory
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #/flaskr/db.py database initialization & connection
    from . import db
    db.init_app(app)

    #/flaskr/auth.py blueprint includes: register, login, logout, auth checks
    from . import auth
    app.register_blueprint(auth.bp)

    #/flaskr/collection.py blueprint includes: create, view, update, delete
    from . import collection
    app.register_blueprint(collection.bp)

    #set default route to collection index
    app.add_url_rule('/', endpoint='index')


    return app