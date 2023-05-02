import pyodbc
from datetime import datetime, timedelta
import random
import math

############ IN ##################################################################################################################################################################

# Azure bellow ///////////////////////
server_name = 'parkpal-server.database.windows.net'
database_name = 'ParkingDb'
username = 'parkpal-admin'
password = 'Password123'

connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server='+server_name+';Database='+database_name+';UID='+username+';PWD='+password+';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

# # Connection to the database
conn = pyodbc.connect(connection_string)


# SQL bellow /////////////////////////////
# Connect to the database using Windows authentication
#conn = pyodbc.connect('Driver={SQL Server};'
#                      'Server=DESKTOP-N1GVVS5\MSSQLSERVER01;'
#                      'Database=your_parking;'
#                      'Trusted_Connection=yes;')

# Create a cursor to execute SQL queries
cursor = conn.cursor()


# SQL above /////////////////////////////

# Entry functions
def car_entry(num_entries_per_day=[70, 50, 50, 30, 30, 70, 50]):
	def create_table():
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
		rego = f"AB{random.randint(1, 99):02d}CD"
		return rego

	def get_temp(num_entries_per_day, month, day, hour, minute):
		base_temp = round(random.uniform(6, 25), 1)
		if num_entries_per_day > 70 and base_temp < 20:
			base_temp = round(random.uniform(20, 25), 1)
		if num_entries_per_day > 50 and base_temp < 15:
			base_temp = round(random.uniform(15, 20), 1)
		if num_entries_per_day > 30 and base_temp < 9:
			base_temp = round(random.uniform(9, 15), 1)

		temp_variation = 0
		for i in range(1, 2):
			temp_variation += random.uniform(-0.5, 0.5) * math.sin(
				2 * math.pi * day / 28 * i + (hour + minute / 60) / 12 * math.pi)
		temp_variation *= 0.5

		temp = round(base_temp + temp_variation, 1)

		return temp

	def get_humid(num_entries_per_day, month, day, hour, minute):
		base_temp = get_temp(num_entries_per_day, month, day, hour, minute)
		humid = round(random.uniform(0, 40), 1)
		if base_temp <= 0:
			humid = min(humid, 40)

		humid_variation = 0
		for i in range(1, 3):
			humid_variation += random.uniform(-0.1, 0.1) * math.sin(
				2 * math.pi * day / 28 * i + (hour + minute / 60) / 12 * math.pi)
		humid_variation *= 0.3

		humid += humid_variation
		humid = max(0, min(humid, 40))

		return round(humid, 1)

	def get_time_entry(month=None):
		if month is None:
			month = random.randint(1, 12)
		year = 2023
		day = random.randint(1, 28)
		hour = random.randint(8, 19)
		minute = random.randint(0, 59)
		second = random.randint(0, 59)
		time_entry = datetime(year, month, day, hour, minute, second)
		return time_entry.strftime('%Y-%m-%d %H:%M:%S')

	def insert_row(day, hour, minute):
		rego = get_rego()
		temp = get_temp(num_entries_per_day=num_entries_per_day[day - 1], month=1, day=day, hour=hour, minute=minute)
		humid = get_humid(num_entries_per_day=num_entries_per_day[day - 1], month=1, day=day, hour=hour, minute=minute)
		time_entry = get_time_entry(month=1)  # Specify the month here
		is_parked = 1
		insert_row_sql = f"INSERT INTO parking_table (rego, temp, humid, time_entry, is_parked) VALUES ('{rego}', {temp}, {humid}, '{time_entry}', {is_parked})"
		cursor.execute(insert_row_sql)
		conn.commit()

	def select_all_rows():
		cursor.execute(
			'SELECT ROW_NUMBER() OVER (ORDER BY time_entry ASC) AS id, rego, temp, humid, time_entry, is_parked FROM parking_table')
		for row in cursor.fetchall():
			print(row)

	create_table()

	for i in range(1):
		for day, num_entries in enumerate(num_entries_per_day, start=1):
			for j in range(num_entries):
				hour = random.randint(8, 19)
				minute = random.randint(0, 59)
				insert_row(day, hour, minute)

	select_all_rows()

	# Close the cursor and connection
	cursor.close()
	conn.close()


car_entry()


############# TEST EXIT BELLOW ################################################################################################################################################################

def car_exit():
	# Connect back to Azure
	conn = pyodbc.connect(connection_string)
	cursor = conn.cursor()

	# SQL bellow /////////////////////////////
	# Connect to the database using Windows authentication
	conn = pyodbc.connect('Driver={SQL Server};'
	                      'Server=DESKTOP-N1GVVS5\MSSQLSERVER01;'
	                      'Database=your_parking;'
	                      'Trusted_Connection=yes;')

	# Create a cursor to execute SQL queries
	cursor = conn.cursor()

	# SQL above /////////////////////////////

	def add_columns():
		cursor.execute('''
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'parking_table' AND COLUMN_NAME = 'time_exit')
            BEGIN
                ALTER TABLE parking_table ADD time_exit DATETIME NULL;
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
		cursor.execute("SELECT id, time_entry FROM parking_table WHERE is_parked=1")
		rows = cursor.fetchall()
		for row in rows:
			id, time_entry = row
			time_exit = time_entry + timedelta(minutes=random.randint(60, 600))  # 1-10 hours
			while time_exit.hour >= 20:
				time_exit = time_entry + timedelta(minutes=random.randint(60, 600))
			time_exit_str = time_exit.strftime('%Y-%m-%d %H:%M:%S')
			time_diff = int((time_exit - time_entry).total_seconds() / 3600)  # in hours
			is_parked = 0
			update_row_sql = f"UPDATE parking_table SET time_exit='{time_exit_str}', time_diff={time_diff}, is_parked={is_parked} WHERE id={id}"
			cursor.execute(update_row_sql)
		conn.commit()

	add_columns()

	update_parking_table()

	cursor.execute("SELECT * FROM parking_table ORDER BY time_entry ASC")
	rows = cursor.fetchall()
	for row in rows:
		print(row)

	cursor.close()
	conn.close()


car_exit()