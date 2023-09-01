import mysql.connector
import datetime
import json

host = 'localhost'
user = 'root'
password = ''
database = 'facultyleavedb'

conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
cursor = conn.cursor()
id = str(input("enter the id"))

query = "SELECT * FROM `staff` WHERE id=" + id + ";"
cursor.execute(query)
data = cursor.fetchall()

cursor.reset()
query = "SELECT `from`, `to`, `with_permission_on`, `date_of_rejoin`, `total` FROM `el` WHERE id=" + id + "; "
cursor.execute(query)
data2 = cursor.fetchall()
data2
data_el = [sublist + ("el",) for sublist in data2]

cursor.reset()
query = "SELECT `from`, `to`, `medical_fittness_on`, `with_permission_on`, `doj`, `total` FROM `lop` WHERE id=" + id + "; "
cursor.execute(query)
data3 = cursor.fetchall()
data_lop = [sublist + ("lop",) for sublist in data3]

cursor.reset()
query = "SELECT `from`, `to`, `medical_fittness_on`, `with_permission_on`, `doj`, `total` FROM `ml` WHERE id=" + id + "; "
cursor.execute(query)
data4 = cursor.fetchall()
data_ml = [sublist + ("ml",) for sublist in data4]

cursor.reset()
query = "SELECT `from`, `to`, `medical_fittness_on`, `with_permission_on`, `doj`, `total` FROM `mtl` WHERE id=" + id + "; "
cursor.execute(query)
data5 = cursor.fetchall()
data_mtl = [sublist + ("mtl",) for sublist in data5]

sorted_data = sorted(data_lop + data_el + data_ml + data_mtl, key=lambda x: x[0])
for item in sorted_data:
    print(item)

import xlsxwriter

workbook = xlsxwriter.Workbook('Book.xlsx')
worksheet = workbook.add_worksheet()
worksheet.set_column('A:M', 12)

abbreviations = {
    "ece": "Electronics and Communication Engineering",
    "cse": "Computer Science and Engineering",
    "geo": "Geology",
    "mech": "Mechanical Engineering",
    "mba": "Master of Business Administration",
    "mca": "Master of Computer Applications"
}

merge_ranges = [
    (2, 0, 2, 3),
    (2, 4, 2, 12),
    (3, 0, 3, 3),
    (3, 4, 3, 12),
    (4, 0, 4, 3),
    (4, 4, 4, 12),
    (5, 0, 5, 3),
    (5, 4, 5, 12),
    (6, 0, 6, 3),
    (6, 4, 6, 12),
    (7, 0, 7, 12),
    (8, 0, 8, 4),
    (8, 5, 8, 10)

]
cell_format_center = workbook.add_format({
    'align': 'center',  # Center alignment
    'text_wrap': True,  # Wrap text

})
cell_format_left = workbook.add_format({
    'align': 'center',  # Center alignment
    'text_wrap': True,  # Wrap text

})

# Perform the defined merges
worksheet.merge_range(*(0, 0, 0, 12), 'Annexure -II', cell_format_center)
worksheet.merge_range(*(1, 0, 1, 12), 'Anna univeristy chennai', cell_format_center)
worksheet.merge_range(*merge_ranges[0], 'Name', cell_format_center)
worksheet.merge_range(*merge_ranges[1], data[0][1], cell_format_left)
worksheet.merge_range(*merge_ranges[2], 'Designation', cell_format_left)
worksheet.merge_range(*merge_ranges[3], '', cell_format_left)
worksheet.merge_range(*merge_ranges[4], 'Department', cell_format_left)
worksheet.merge_range(*merge_ranges[5], abbreviations[data[0][2].lower()], cell_format_left)
worksheet.merge_range(*merge_ranges[6], 'Date of joining in service', cell_format_left)
worksheet.merge_range(*merge_ranges[7], data[0][3].strftime('%d-%m-%Y'), cell_format_left)
worksheet.merge_range(*merge_ranges[8], 'Campus', cell_format_left)
worksheet.merge_range(*merge_ranges[9], 'ANNA UNIVERSITY REGIONAL CAMPUS   -   TIRUNELVELI', cell_format_center)
worksheet.merge_range(*merge_ranges[10], 'DETAILS OF LEAVE', cell_format_left)
worksheet.merge_range(*merge_ranges[11], 'Earned Leave  (EL)', cell_format_left)
worksheet.merge_range(*merge_ranges[12], 'Medical Leave  (ML)  /  Maternity Leave  (MTL) / Loss of pay (LOP)',
                      cell_format_left)
worksheet.write('L9', 'Typeofleave', cell_format_left)
worksheet.write('M10', 'Remarks', cell_format_left)

head_list = [['From', 'To', 'with permission on', 'Date of Joining on Duty after EL', 'Total No. of Days',
              'From', 'To', 'Total No. of Days', 'Medical Fitness on', 'with permission on',
              'Date of Joining on Duty after leave', '(ML/ EL/LOP/MTL)']
             ]

# Define the starting row
start_row = 9

# Iterate through each sublist and its values
for sublist in head_list:
    column_index = 0  # Start writing from the first column
    for value in sublist:
        worksheet.write(start_row, column_index, value, cell_format_left)
        column_index += 1  # Move to the next column for the next value
    start_row += 1

start_row = 10
for sublist in sorted_data:
    # Start writing from the first column
    if sublist[-1] == 'el':
        column_index = 0
        for value in sublist:
            if value == 'el':
                worksheet.write(start_row, 11, value, cell_format_left)
            elif isinstance(value, datetime.date):
                worksheet.write(start_row, column_index, value.strftime('%d-%m-%Y'), cell_format_left)
                column_index += 1
            elif isinstance(value, bytes):
                byte_data = value
                byte_data_str = byte_data.decode('utf-8')
                str_data = json.loads(byte_data_str)
                worksheet.write(start_row, column_index, str_data[0], cell_format_left)
                column_index += 1

            else:
                worksheet.write(start_row, column_index, value, cell_format_left)
                column_index += 1  # Move to the next column for the next value
        for i in range(column_index, 11):
            worksheet.write(start_row, i, "-", cell_format_center)

        start_row += 1
    else:
        column_index = 5
        for value in sublist:
            if value == 'lop':
                worksheet.write(start_row, 11, value, cell_format_left)
            elif isinstance(value, datetime.date):
                worksheet.write(start_row, column_index, value.strftime('%d-%m-%Y'), cell_format_left)
                column_index += 1
            elif isinstance(value, bytes):
                byte_data = value
                byte_data_str = byte_data.decode('utf-8')
                str_data = json.loads(byte_data_str)
                worksheet.write(start_row, column_index, str_data[0], cell_format_left)
                column_index += 1

            else:
                worksheet.write(start_row, column_index, value, cell_format_left)
                column_index += 1  # Move to the next column for the next value
        for i in range(0, 6):
            worksheet.write(start_row, i, "-", cell_format_center)

        start_row += 1

workbook.close()

# timepass
import subprocess
import os

subprocess.Popen(["book.xlsx"], shell=True)
input("Press Enter after you've closed the Excel file...")
os.remove("book.xlsx")