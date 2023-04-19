import psycopg2
import pandas as pd

from .process_sql import _get_app_db_conn_


def get_df_from_tablename(tablename):

    # Connect to Postgres database
    # ToDo: remove query execution from here
    conn = _get_app_db_conn_()
    # Query the database
    query = f"SELECT * FROM {tablename};"
    df = pd.read_sql(query, conn)

    # Close the database connection
    conn.close()
    return df