#coding=utf8

import os

port = 8080

db_config = {
    'dialect': 'mysql',
    'driver': 'mysqldb',
    'username': 'internal',
    'password': 'nodemix',
    #'host': 'localhost',
    'host': '10.10.10.100',
    'port': 3306,
    'database': 'docky',
    'debug': False,
}

mongodb_config = {
    #'host': 'localhost',
    'host': '10.10.10.100',
    'port': 27017,
    'name': 'docky',
}

debug = True

root = os.path.abspath(os.path.dirname(__file__))

template_path = os.path.join(root, 'templates')

static_path = os.path.join(root, 'static')

# user auth
auth_secret = '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo='
auth_name = 'user_id' # not used yet
web_auth_key = 'user'

if '__main__' == __name__:
    # TODO use command line args to control action
    import app
    app.load_package()

    from models import db

    print 'creating database table structure..'
    db.create_db(admin=True)
    print 'done'
