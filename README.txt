ParkingApp

The ParkingApp is an application that utilizes data to anticipate peak and off-peak parking lot usage times based on a dataset inputted from an Azure database. The software also employs a categorizing pricing function to compute the cost of car park entry.

Installation

To access this program you should have the following Python libraries installed:

- np
- pd 
- pyodbc
- sns 
- plt  
- sklearn 
- datetime 
- sqlalchemy

Execute the installation using pip in the command prompt:

bash
pip install numpy pandas pyodbc seaborn matplotlib scikit-learn datetime sqlalchemy
```

Usage 

Accessing property in an Azure database with python, through 'pyodbc' library is essential for utilizing this app. To enable working within your specific database edit variables `server_name`, `database_name`, `username`, and `password`: 
 
```
server_name = 'parkpal-server.database.windows.net'
database_name = 'ParkingDb'
username = 'parkpal-admin'
password = 'Password123'

connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=' + server_name + ';Database=' + database_name + ';UID=' + username + ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
conn = pyodbc.connect(connection_string)
```

Afterwards, execute a query on the table `'parking_table'` within the database: 

```
query = "SELECT * FROM parking_table"
df = pd.read_sql_query(query, conn)
```

Predictions about whether customers would spend more than 4 hours or not, this can be performed by running the sample code below. Utilizing `scikit-learn` which trains and evaluates machine learning models, both `LinearRegression` and `LogisticRegression`.
 
```
df['weekday'] = pd.to_datetime(df['time_entry']).dt.weekday 
X = df[['time_diff', 'temp', 'humid', 'weekday']]
y = (df['time_diff'] >= 4) & (df['weekday'] < 5) 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)


predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
print("Model Accuracy:", accuracy)

cm = confusion_matrix(y_test, predictions)
sns.heatmap(cm, annot=True, fmt='g')
plt.title('Likelihood of a customer spending more than 4 hours on a weekday')
plt.show()
```

To anticipate non-peak and peak usage times using a `LinearRegression` model:
```
X = df[['time_diff', 'temp', 'humid']]
y = df['is_parked']

# Splitting the data into training and testing sets

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = LinearRegression()

model.fit(X_train, y_train)

predictions = model.predict(X_test)

score = model.score(X_test, y_test)
```

Usage:
This code is a Python script that connects to a SQL database and performs some data analysis and machine learning tasks on a parking dataset.

First, the necessary libraries and packages are imported, including numpy, pandas, pyodbc, seaborn, matplotlib, sklearn, and datetime.

Next, a connection is established to the SQL database using pyodbc and a SQL query is executed to retrieve all the rows from a table called "parking_table". The resulting data is stored in a pandas DataFrame called "df".

The code then creates a linear regression model using the "time_diff", "temp", and "humid" columns as features and "is_parked" column as the target variable. The data is split into training and testing sets, and the model is trained on the training set and evaluated on the testing set. The model score is printed to the console.

The code then creates a logistic regression model to predict whether a customer will spend more than 4 hours in the parking lot on a weekday or weekend. The data is split into training and testing sets, and the model is trained on the training set and evaluated on the testing set. The model accuracy is printed to the console, and a confusion matrix is created to visualize the results.

Finally, the code creates a heatmap visualization of the peak usage of the parking lot by day of the week and hour of the day. The code also calculates the price based on the peak usage.