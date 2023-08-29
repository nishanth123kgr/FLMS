import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(host="localhost", port="3306", user="root",
                               database="facultyleavedb")

mycursor = mydb.cursor()

data = pd.read_excel("staffs.xlsx")
data = data.drop(data.columns[-1], axis=1)
data = data.drop(data.columns[0], axis=1)
data['Date Of Join'] = data['Date Of Join'].dt.strftime('%Y-%m-%d')
data = data.values.tolist()

for i in data:
    mycursor.execute("INSERT INTO staff (name, id, doj, department) VALUES (%s, %s, %s, %s)", (i[0], i[1], i[2], i[3]))
    mydb.commit()
    mycursor.reset()
