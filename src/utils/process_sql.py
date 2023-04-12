import io
import logging

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .sql_constants import *

def _get_app_db_conn_(dbname=APP_DB_NAME, db_user=DB_USER, db_password=DB_PASS, db_host=DB_HOST, db_port=DB_PORT):
    
    # Connect to the database
    conn = psycopg2.connect(
        dbname=dbname,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    if conn is None:
        raise Exception('Connection could not be made')

    return conn

def _execute_sql_(sql, conn=None):

    if conn is None:
       conn =  _get_app_db_conn_(dbname=APP_DB_NAME)

    cur = conn.cursor()
    
    cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()


def app_db_present():
    conn = _get_app_db_conn_(dbname=DEFAULT_DB_NAME)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (APP_DB_NAME,))
    exists = cur.fetchone()
    return exists

def create_app_db():
    if not app_db_present():
        logging.info('Creating database')
        conn = _get_app_db_conn_(dbname=DEFAULT_DB_NAME)
        conn.autocommit=True
        _execute_sql_(sql=f'CREATE DATABASE {APP_DB_NAME};', conn=conn)
        logging.info('Database created')
    logging.info('App database already present')


def del_app_db():
    if app_db_present():
        conn = _get_app_db_conn_(dbname=DEFAULT_DB_NAME)
        conn.autocommit=True
        _execute_sql_(sql=f'DROP DATABASE {APP_DB_NAME};', conn=conn)


def execute_sql_file(sql_file, db_name, db_user, db_password, db_host, db_port):
    # Open the SQL file and read its contents
    with open(sql_file, 'r') as f:
        sql = f.read()

    conn = _get_app_db_conn_(dbname=APP_DB_NAME)
    _execute_sql_(sql=sql, conn=conn)

def execute_sql_stream(sql):
    conn = _get_app_db_conn_(dbname=APP_DB_NAME)
    _execute_sql_(sql=sql, conn=conn)



def execute_sql_string(sql_string, db_name, db_user, db_password, db_host, db_port):
    # Convert the SQL string to a byte stream
    sql_bytes = io.BytesIO(sql_string.encode())

    # Call the execute_sql_file method with the byte stream input
    execute_sql_file(sql_bytes, db_name, db_user, db_password, db_host, db_port)


def get_tables_from_app_db():
    conn = _get_app_db_conn_(dbname=APP_DB_NAME)
    # get the list of table names
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    table_names = [row[0] for row in cur.fetchall()]
    cur.close()
    # close the connection
    conn.close()
    return table_names
