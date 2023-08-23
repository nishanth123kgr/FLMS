import mysql.connector

mydb = mysql.connector.connect(host="localhost", port="3306", user="root",
                               database="facultyleavedb")

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM staff")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)
