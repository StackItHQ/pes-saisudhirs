import json
from datetime import datetime

import mysql.connector


def get_mysql_connection():
    with open('secrets.json') as f:
        config = json.load(f)

    connection = mysql.connector.connect(host=config['mysql']['host'], database=config['mysql']['database'],
                                         user=config['mysql']['user'], password=config['mysql']['password'])
    return connection


def create_table(cursor, table_name, num_columns):
    columns_def = ', '.join([f"col{i + 1} VARCHAR(255)" for i in range(num_columns)])
    drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
    cursor.execute(drop_table_query)
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT NOT NULL AUTO_INCREMENT UNIQUE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        {columns_def},
        PRIMARY KEY (id)
    );
    """
    cursor.execute(create_table_query)


def create_sync_table(cursor):
    create_sync_query = """
    CREATE TABLE IF NOT EXISTS sync_info (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        last_sync TIMESTAMP DEFAULT '1970-01-01 00:00:00'
    );
    """
    cursor.execute(create_sync_query)


def get_db_last_update(cursor, table_name):
    cursor.execute(f"SELECT MAX(timestamp) FROM {table_name}")
    result = cursor.fetchone()
    return result[0] if result[0] else None


def update_last_sync_time(cursor, connection):
    last_sync = datetime.now().isoformat()
    cursor.execute("DELETE FROM sync_info;")
    cursor.execute("INSERT INTO sync_info (last_sync) VALUES (%s);", (last_sync,))
    connection.commit()


def fetch_all_data(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    return cursor.fetchall()
