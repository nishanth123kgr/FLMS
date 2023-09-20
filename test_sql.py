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


# import re
#
# # Sample string containing dates
# text = "08.12.2018, & 09.12.2018"
#
# # Define a regular expression pattern to match dates in various formats
# date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{2}|\d{2}-\d{2}-\d{4}|[0-9]{2}.[0-9]{2}.[0-9]{4}'
#
# # Find all dates in the string
# dates = re.findall(date_pattern, text)
#
# # Print the found dates
# for date in dates:
#     print(date)


# import datetime
#
# date_ranges = [['2010-01-09', '2010-01-13'],  # ['2010-01-14', '2010-01-17'],
#                ['2010-01-18', '2010-01-22'], ['2010-01-26', '2010-01-28'], ['2010-01-29', '2010-02-07']]
#
#
# def srt(dates):
#     return dates[0]
#
#
# prevented_dates = date_ranges.copy()
#
#
# def get_missing_dates(prevented_dates):
#     for i in range(1, len(date_ranges)):
#         nxt = datetime.datetime.strptime(date_ranges[i - 1][1], "%Y-%m-%d") + datetime.timedelta(days=1)
#         if nxt != datetime.datetime.strptime(date_ranges[i][0], "%Y-%m-%d"):
#             prevented_dates += [[nxt.strftime("%Y-%m-%d"),
#                                  (datetime.datetime.strptime(date_ranges[i][0], "%Y-%m-%d") - datetime.timedelta(
#                                      days=1)).strftime(
#                                      "%Y-%m-%d")]]
#
#     return sorted(prevented_dates, key=srt)


import datetime

# Sample nested dictionary
data = {
    '09-10s': {
        'from': [datetime.date(2010, 5, 28)],
        'to': [datetime.date(2010, 7, 11)],
        'Availed_from': [datetime.date(2010, 6, 9)],
        'Availed_to': [datetime.date(2010, 7, 11)],
        'Prevented': [['2010-05-28', '2010-06-08']]
    },
    '09-10w': {
        'from': [datetime.date(2010, 1, 9), datetime.date(2010, 1, 9)],
        'to': [datetime.date(2010, 2, 7), datetime.date(2010, 2, 7)],
        'Availed_from': [datetime.date(2010, 1, 14), datetime.date(2010, 1, 29)],
        'Availed_to': [datetime.date(2010, 1, 17), datetime.date(2010, 2, 7)],
        'Prevented': [['2010-01-09', '2010-01-13'], ['2010-01-18', '2010-01-28']]
    },
    # Add more entries as needed
}

# Function to convert datetime.date to formatted date text


# Apply the conversion to all values in the nested dictionary
for key, value in data.items():
    data[key] = {inner_key: convert_to_date_text(inner_value) for inner_key, inner_value in value.items()}

# Print the converted nested dictionary
print(data)