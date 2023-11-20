import mysql.connector
import pandas as pd
import datetime
import ast
import json

def get_date_of_join(cursor, id):
    query = 'select doj from staff where id=%s' % (id)
    cursor.execute(query)
    date_of_join = cursor.fetchall()
    cursor.reset()
    date_of_join = date_of_join[0][0]
    return date_of_join

def leave_availed(cursor, id, type, from_date, to_date):
    query = "SELECT `from`, `to` FROM %s WHERE id = %s AND `from` >= '%s' AND `to` <= '%s';" % (type, id, from_date, to_date)
    cursor.execute(query)
    leave_availed = cursor.fetchall()
    cursor.reset()
    return leave_availed


if __name__ == '__main__':
    db = mysql.connector.connect(host="localhost", port="3306", user="root", database="facultyleavedb")
    cursor = db.cursor()
    id = '22009'
    date_of_join = pd.to_datetime(get_date_of_join(cursor, id))
    print(date_of_join)
    from_date_range = pd.date_range(start=date_of_join, end=f'{datetime.datetime.now().year-1}-07-01', freq='AS-JUL').tolist()
    from_date_range.insert(0, date_of_join)
    date_range = pd.date_range(start='2010-06-30', end=f'{datetime.datetime.now().year}-06-30', freq='A-JUN')

    # Filter the date range based on date_of_join
    to_date_range = date_range[date_range > date_of_join]
    # print(from_date_range)
    # # Display the filtered dates
    # print(to_date_range)
    # Create a dataframe with the date range
    df = pd.DataFrame({'from': from_date_range, 'to': to_date_range})
    print(df)
    table = pd.DataFrame()
    for i in range(len(df)):
        leaves = []
        for type in ['el', 'ml', 'mtl', 'lop']:
            leaves.extend(leave_availed(cursor, id, type, df.at[i, 'from'], df.at[i, 'to']))
        
        print('\n',leaves, end='\n\n\n\n')
        leaves = sorted(leaves, key=lambda x: x[0])
        table.at[i, 'from'] = df.at[i, 'from']
        if leaves:
            table.at[i, 'to'] = leaves[0][0] - datetime.timedelta(days=1)
            for j in range(1, len(leaves)):
                table.at[i+j, 'from'] = leaves[j-1][1] + datetime.timedelta(days=1)
                table.at[i+j, 'to'] = leaves[j][0] - datetime.timedelta(days=1)
        else:
            table.at[i, 'to'] = df.at[i, 'to']
    print(table)