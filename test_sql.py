import mysql.connector
import pandas as pd

#
mydb = mysql.connector.connect(host="localhost", port="3306", user="root",
                               database="facultyleavedb")

mycursor = mydb.cursor()
#
# data = pd.read_excel("staffs.xlsx")
# data = data.drop(data.columns[-1], axis=1)
# data = data.drop(data.columns[0], axis=1)
# data['Date Of Join'] = data['Date Of Join'].dt.strftime('%Y-%m-%d')
# data = data.values.tolist()
#
# for i in data:
#     mycursor.execute("INSERT INTO staff (name, id, doj, department) VALUES (%s, %s, %s, %s)", (i[0], i[1], i[2], i[3]))
#     mydb.commit()
#     mycursor.reset()

sheets = pd.ExcelFile('attend- register -09.07.2023.xlsx').sheet_names
print(sheets)
for i in sheets:
    data = pd.read_excel('attend- register -09.07.2023.xlsx', sheet_name=i)
    data = data.drop(data.columns[0], axis=1).drop([0, 1]).reset_index().drop("index", axis=1)
    print(data.values.tolist())
    for row in data.values.tolist():
        mycursor.execute("INSERT INTO attendance_register (department, year, register_name) VALUES (%s, %s, %s)",
                         (i.upper(), row[0], row[1]))
        mydb.commit()
        mycursor.reset()
