import pyodbc
from datetime import datetime, timedelta
import random
import math

server_name = 'parkpal-server.database.windows.net'
database_name = 'ParkingDb'
username = 'parkpal-admin'
password = 'Password123'

connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=' + server_name + ';Database=' + database_name + ';UID=' + username + ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

conn = pyodbc.connect(connection_string)

cursor = conn.cursor()


def create_price_table():
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[price_table]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [dbo].[price_table](
                [id] [int] IDENTITY(1,1) NOT NULL,
                [price] [float] NOT NULL,
            )
        END
    ''')
    conn.commit()


create_price_table()


def car_entry():
    def create_parking_table():
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[parking_table]') AND type in (N'U'))
            BEGIN
                CREATE TABLE [dbo].[parking_table](
                    [id] [int] IDENTITY(1,1) NOT NULL,
                    [rego] [nvarchar](50) NOT NULL,
                    [temp] [float] NOT NULL,
                    [humid] [float] NOT NULL,
                    [time_entry] [datetime] NOT NULL,
                    [is_parked] [int] NULL
                )
            END
        ''')
        conn.commit()

    def get_rego():
        rego = input("Enter registration number: ")  # cam
        return rego

    def get_temp():
        temp = float(input("Enter temperature: "))  # temp
        return temp

    def get_humid():
        humid = float(input("Enter humidity: "))  # humid
        return humid

    def get_time_entry():
        time_entry = datetime.now().replace(microsecond=0)  # Datetime without milliseconds
        return time_entry.strftime('%Y-%m-%d %H:%M:%S')

    def insert_row(rego, temp, humid):
        time_entry = get_time_entry()
        is_parked = 1
        insert_row_sql = f"INSERT INTO parking_table (rego, temp, humid, time_entry, is_parked) VALUES ('{rego}', {temp}, {humid}, '{time_entry}', {is_parked})"
        cursor.execute(insert_row_sql)
        conn.commit()

    def select_all_rows():
        cursor.execute(
            'SELECT ROW_NUMBER() OVER (ORDER BY time_entry ASC) AS id, rego, temp, humid, time_entry, is_parked FROM parking_table')
        for row in cursor.fetchall():
            print(row)

    create_parking_table()
    rego = get_rego()
    temp = get_temp()
    humid = get_humid()
    insert_row(rego, temp, humid)
    select_all_rows()

    cursor.close()
    conn.close()


car_entry()


#############

def get_exit_reg():
    return "AB66CD"


def car_exit():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    def add_columns():
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'parking_table' AND COLUMN_NAME = 'time_exit')
            BEGIN
                ALTER TABLE parking_table ADD time_exit DATETIME2(0) NULL;
            END

            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'parking_table' AND COLUMN_NAME = 'time_diff')
            BEGIN
                ALTER TABLE parking_table ADD time_diff INT NULL;
            END

            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'parking_table' AND COLUMN_NAME = 'is_parked')
            BEGIN
                ALTER TABLE parking_table ADD is_parked BIT NOT NULL DEFAULT 1;
            END
        ''')
        conn.commit()

    def update_parking_table():
        rego = get_exit_reg()
        cursor.execute("SELECT id, time_entry FROM parking_table WHERE is_parked=1 AND rego=?", (rego,))
        row = cursor.fetchone()
        if row:
            id, time_entry = row
            time_exit = datetime.now().replace(microsecond=0)  # Datetime without milliseconds
            time_diff = int((time_exit - time_entry).total_seconds() / 3600)  # in hours
            is_parked = 0
            update_row_sql = "UPDATE parking_table SET time_exit=?, time_diff=?, is_parked=? WHERE id=?"
            cursor.execute(update_row_sql, (time_exit, time_diff, is_parked, id))

            conn.commit()
        else:
            print(f"No parked cars found with rego: {rego}")

    add_columns()

    update_parking_table()

    cursor.execute("SELECT * FROM parking_table ORDER BY time_entry ASC")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()


car_exit()


#############

def read_database():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parking_table ORDER BY time_entry ASC")
    rows = cursor.fetchall()

    data = []
    for row in rows:
        id, rego, temp, humid, time_entry, is_parked, time_exit, time_diff = row
        row_dict = {
            'id': id,
            'rego': rego,
            'temp': temp,
            'humid': humid,
            'time_entry': time_entry,
            'time_exit': time_exit,
            'time_diff': time_diff,
            'is_parked': is_parked
        }
        data.append(row_dict)

    cursor.close()
    conn.close()

    return data


data = read_database()
for row in data:
    print("Rego:", row['rego'], "Temp:", row['temp'], "Humid:", row['humid'], "Entry:", row['time_entry'], "Exit:",
          row['time_exit'], "Duration:", row['time_diff'], "Status:", row['is_parked'])
