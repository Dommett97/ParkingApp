import pyodbc
from datetime import datetime, timedelta
import random

# Connect to the database using Windows authentication
conn = pyodbc.connect('Driver={SQL Server};'
                       'Server=DESKTOP-7BVPIF1;'
                       'Database=your_parking;'
                       'Trusted_Connection=yes;')

# # Create a cursor to execute SQL queries
cursor = conn.cursor()


# Entry functions
def car_exit():
    def create_table():
         cursor.execute('''
             IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[exit_table]') AND type in (N'U'))
             BEGIN
                 CREATE TABLE [dbo].[exit_table](
                     [id] [int] IDENTITY(1,1) NOT NULL,
                     [rego] [nvarchar](50) NOT NULL,
                     [temp] [float] NOT NULL,
                     [humid] [float] NOT NULL,
                     [time_entry] [datetime] NOT NULL,
                     [time_exit] [datetime] NOT NULL,
                     [time_diff] [float] NOT NULL,
                     [is_parked] [int] NULL
                 )
             END
         ''')
         conn.commit()

    # Function to insert a new row into the table
    def insert_row(rego, temp, humid, time_entry, time_exit, is_parked):
         time_diff = get_time_diff(time_entry, time_exit)
         cursor.execute(
             'INSERT INTO exit_table (rego, temp, humid, time_entry, time_exit, time_diff, is_parked) VALUES (?, ?, ?, ?, ?, ?, ?)',
             (rego, temp, humid, time_entry, time_exit, time_diff, is_parked)
         )
         conn.commit()

    # Function to update an existing row in the table
    def update_row(id, rego, temp, humid, time_entry, time_exit, is_parked):
         time_diff = get_time_diff(time_entry, time_exit)
         cursor.execute('UPDATE exit_table '
                     'SET rego = ?, '
                     'temp = ?, '
                     'humid = ?, '
                     'time_entry = ?, '
                     'time_exit = ?, '
                     'time_diff = ?, '
                     'is_parked = ? '
                     'WHERE id = ?',
                     (rego, temp, humid, time_entry, time_exit, time_diff, is_parked, id))
         conn.commit()

    # Function to delete an existing row from the table
    def delete_row(id):
         cursor.execute('DELETE FROM exit_table '
                     'WHERE id = ?',
                     (id,))
         conn.commit()

    # Function to select all rows from the table and print them
    def select_all_rows():
         cursor.execute('SELECT * FROM exit_table')
         for row in cursor.fetchall():
             print(row)

    # Function to calculate the time difference between two datetime objects in hours and minutes
    def get_time_diff(start_time, end_time):
         time_diff = end_time - start_time

         sec = time_diff.total_seconds()
         minutes = sec / 60
         hours = sec / (60 * 60)

         # seconds = seconds % 60
         return hours + minutes

    # Create the table if it doesn't exist
    create_table()

    is_parked  = 0

    # Insert a new row
    insert_row('NU04TVA', 10.5, 10.5, datetime.datetime(2022, 1, 1), datetime.datetime.now(), is_parked)
    insert_row('NU04TVB', 20.5, 10.5, datetime.datetime(2022, 2, 1), datetime.datetime.now(), is_parked)
    insert_row('NU04TVC', 30.5, 10.5, datetime.datetime(2022, 3, 1), datetime.datetime.now(), is_parked)

    # Update the row with id 1
    update_row(1, 'test string', 1.0, 2.0, datetime.datetime.now(), datetime.datetime.now(), is_parked)

    # Delete the row with id 2
    delete_row(2)
    # Select all rows and print them
    select_all_rows()
    # Close the cursor and connection
    cursor.close()
    conn.close()

car_exit()
