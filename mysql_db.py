import json

import mysql.connector
from mysql.connector import Error

def get_mysql_connection():
    with open('secrets.json') as f:
        secrets = json.load(f)

    connection = mysql.connector.connect(
        host=secrets['mysql']['host'],
        database=secrets['mysql']['database'],
        user=secrets['mysql']['user'],
        password=secrets['mysql']['password']
    )
    return connection

def create_table(cursor, table_name, num_columns):
    columns_def = ', '.join([f"col{i + 1} VARCHAR(255)" for i in range(num_columns)])
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT NOT NULL AUTO_INCREMENT UNIQUE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        {columns_def},
        PRIMARY KEY (id)
    );
    """
    cursor.execute(create_table_query)

def upsert_data(cursor, table_name, data):
    num_columns = len(data[0]) if data else 0

    placeholders = ', '.join(['%s'] * num_columns)
    update_placeholders = ', '.join([f"col{i + 1} = %s" for i in range(num_columns)])

    for row in data:
        if not row:
            continue

        # Check for existing row
        check_query = f"SELECT id FROM {table_name} WHERE " + ' AND '.join(
            [f"col{i + 1} = %s" for i in range(num_columns)])
        cursor.execute(check_query, tuple(row))
        result = cursor.fetchone()

        if result:
            # Update existing row
            update_query = f"""
            UPDATE {table_name}
            SET {update_placeholders}, timestamp = CURRENT_TIMESTAMP
            WHERE id = {result[0]};
            """
            try:
                cursor.execute(update_query, tuple(row) + tuple(row))
            except Error as err:
                print(f"Update Error: {err}")
        else:
            # Insert new row
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join([f'col{i + 1}' for i in range(num_columns)])})
            VALUES ({placeholders});
            """
            try:
                cursor.execute(insert_query, tuple(row))
            except Error as err:
                print(f"Insert Error: {err}")
