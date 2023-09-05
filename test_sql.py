# import mysql.connector
# import pandas as pd
#
# mydb = mysql.connector.connect(host="localhost", port="3306", user="root",
#                                database="facultyleavedb")
#
# mycursor = mydb.cursor()
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


import re

# Sample string containing dates
text = "08.12.2018, & 09.12.2018"

# Define a regular expression pattern to match dates in various formats
date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{2}|\d{2}-\d{2}-\d{4}|[0-9]{2}.[0-9]{2}.[0-9]{4}'

# Find all dates in the string
dates = re.findall(date_pattern, text)

# Print the found dates
for date in dates:
    print(date)