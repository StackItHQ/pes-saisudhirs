import time

import mysql

from google_sheet import read_sheet_data, get_sheet_last_update, update_google_sheet
from mysql_db import get_mysql_connection, create_table, upsert_data
from db_utils import create_sync_table, update_last_sync_time, get_db_last_update, fetch_all_data

SPREADSHEET_ID = "1oGTbu5vgawZ9ueal9Dsp_IcsyPKijiRy2q9aGXqYn3g"
RANGE_NAME = "Sheet1"
POLLING_INTERVAL = 10  # seconds


def sync_db_to_sheet(spreadsheet_id, range_name):
    cnx = get_mysql_connection()
    cursor = cnx.cursor()
    try:
        rows = fetch_all_data(cursor, range_name)
        if rows:
            # Convert rows from database to sheet format
            sheet_data = [list(row[1:]) for row in rows]  # Exclude the id column
            update_google_sheet(spreadsheet_id, range_name, sheet_data)
    except mysql.connector.Error as err:
        print(f"DB to Sheet Sync Error: {err}")
    finally:
        cursor.close()
        cnx.close()


def sync_google_sheet_to_db(spreadsheet_id, range_name):
    sheet_data = read_sheet_data(spreadsheet_id, range_name)
    cnx = get_mysql_connection()
    cursor = cnx.cursor()

    try:
        num_columns = max(len(row) for row in sheet_data if row) if sheet_data else 0
        create_table(cursor, range_name, num_columns)
        processed_data = [[None if cell == '' else cell for cell in row] for row in sheet_data]
        upsert_data(cursor, range_name, processed_data)
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()


def sync_loop():
    last_sync_sheet = None
    last_sync_db = None

    while True:
        try:
            # Check for the last update times
            print("Checking last update times...")
            sheet_last_update = get_sheet_last_update(SPREADSHEET_ID)

            cnx = get_mysql_connection()
            cursor = cnx.cursor()
            db_last_update = get_db_last_update(cursor, RANGE_NAME)
            cursor.close()
            cnx.close()
            print(sheet_last_update, db_last_update)

            # Compare update times and perform sync
            if sheet_last_update and (last_sync_sheet is None or sheet_last_update > last_sync_sheet):
                print("Syncing data from Google Sheets to database...")
                sync_google_sheet_to_db(SPREADSHEET_ID, RANGE_NAME)
                last_sync_sheet = sheet_last_update

            if db_last_update and (last_sync_db is None or db_last_update > last_sync_db):
                print("Syncing data from database to Google Sheets...")
                sync_db_to_sheet(SPREADSHEET_ID, RANGE_NAME)
                last_sync_db = db_last_update

            print(f"Next sync in {POLLING_INTERVAL} seconds...")
            time.sleep(POLLING_INTERVAL)
        except Exception as e:
            print(f"Sync Error: {e}")
            time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    sync_loop()
