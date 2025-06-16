# import sqlite3
from datetime import datetime
import pymysql


import click
from flask import current_app, g


# get_db para acesso ao sqlite
# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row

#     return g.db

# get_db para acesso ao mysql
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Para carregar schema do banco em sqlite
# def init_db():
#     db = get_db()

#     with current_app.open_resource('schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))


# Para carregar schema do banco em mysql
def init_db():
    db = get_db()
    with current_app.open_resource('schema_mysql.sql') as f:
        sql_script = f.read().decode('utf8')

    with db.cursor() as cursor:
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
    db.commit()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# sqlite3.register_converter(
#     "timestamp", lambda v: datetime.fromisoformat(v.decode())
# )

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)