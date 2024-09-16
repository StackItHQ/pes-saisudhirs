import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

def get_mysql_connection():
    with open('secrets.json') as f:
        config = json.load(f)

    connection = mysql.connector.connect(
        host=config['mysql']['host'],
        database=config['mysql']['database'],
        user=config['mysql']['user'],
        password=config['mysql']['password']
    )
    return connection

def create_sync_table(cursor):
    create_sync_query = """
    CREATE TABLE IF NOT EXISTS sync_info (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        last_sync TIMESTAMP DEFAULT NULL
    );
    """
    cursor.execute(create_sync_query)

def main():
    cnx = get_mysql_connection()
    cursor = cnx.cursor()
    create_sync_table(cursor)
    cnx.commit()
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    main()
