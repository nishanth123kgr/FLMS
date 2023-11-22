import mysql.connector
import pandas as pd
import datetime
import ast
import json
import math
import xlsxwriter
import os


name = ''
doj = ''
dept = ''


def set_staff_data(cursor, id):
    query = "select doj, name, department from staff where id=%s" % (id)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.reset()
    global name, doj, dept
    name = data[0][1]
    doj = data[0][0]
    dept = data[0][2]


def leave_availed(cursor, id, type, from_date, to_date):
    query = (
            "SELECT `from`, `to` FROM %s WHERE id = %s AND `from` >= '%s' AND `to` <= '%s';"
            % (type, id, from_date, to_date)
    )
    cursor.execute(query)
    leave_availed = cursor.fetchall()
    cursor.reset()
    # print(leave_availed)
    return [[start, end, type] for start, end in leave_availed]


def g(df, leaves, i):
    result = []
    print(leaves)
    if leaves:
        if leaves[0][0].strftime("%d-%m") != "01-07":
            result.append(
                {
                    "from": pd.to_datetime(df.at[i, "from"]).date(),
                    "to": leaves[0][0] - datetime.timedelta(days=1),
                    "type": 0,
                }
            )
        for j in range(1, len(leaves) + 1):
            result.append(
                {
                    "from": leaves[j - 1][0],
                    "to": leaves[j - 1][1],
                    "type": leaves[j - 1][2],
                }
            )
            if j < len(leaves):
                if ((leaves[j][0] - datetime.timedelta(days=1)) - (
                        leaves[j - 1][1] + datetime.timedelta(days=1))).days < 0:
                    continue
                result.append(
                    {
                        "from": leaves[j - 1][1] + datetime.timedelta(days=1),
                        "to": leaves[j][0] - datetime.timedelta(days=1),
                        "type": 0,
                    }
                )
        result.append(
            {
                "from": leaves[-1][1] + datetime.timedelta(days=1),
                "to": pd.to_datetime(df.at[i, "to"]).date(),
                "type": 0,
            }
        )
    else:
        result.append(
            {
                "from": pd.to_datetime(df.at[i, "from"]).date(),
                "to": pd.to_datetime(df.at[i, "to"]).date(),
                "type": 0,
            }
        )
    return result


def calc_vl_prevented_total(to_date, staff_id, cursor):
    year = to_date
    vl_id = f'{str(year - 1)[2:]}-{str(year)[2:]}'
    total_vl = 0
    for i in ['s', 'w']:
        query = 'select prevented from vl where vac_id=\'%s\' and staff_id=%s' % (vl_id + i, staff_id)
        cursor.execute(query)
        prevented = cursor.fetchall()
        cursor.reset()
        if len(prevented) > 0:
            # print(prevented)
            # print(prevented[0][0], type(prevented[0][0]))
            prevented = ast.literal_eval(prevented[0][0].decode('utf-8')) if not isinstance(prevented[0][0],
                                                                                            str) else eval(
                prevented[0][0])
            for i in prevented:
                # print(i)
                if i[0] and i[1]:
                    from_date = datetime.datetime.strptime(i[0], '%Y-%m-%d')
                    to_date = datetime.datetime.strptime(i[1], '%Y-%m-%d')
                    total_vl += (to_date - from_date).days + 1
    return round(total_vl / 3) if total_vl <= 60 else 20


def calculate_leave(id, cursor):
    set_staff_data(cursor, id)
    date_of_join = pd.to_datetime(doj)
    from_date_range = pd.date_range(
        start=date_of_join,
        end=f"{datetime.datetime.now().year - 1}-07-01",
        freq="AS-JUL",
    ).tolist()
    from_date_range.insert(0, date_of_join)
    date_range = pd.date_range(
        start=f"{date_of_join.year}-06-30",
        end=f"{datetime.datetime.now().year}-06-30",
        freq="A-JUN",
    )

    # Filter the date range based on date_of_join
    to_date_range = date_range[date_range > date_of_join]
    df = pd.DataFrame({"from": from_date_range, "to": to_date_range})
    result = []
    for i in range(len(df)):
        leaves = []
        for type in ["el", "ml", "mtl", "lop"]:
            leaves.extend(
                leave_availed(cursor, id, type, df.at[i, "from"], df.at[i, "to"])
            )

        leaves = sorted(leaves, key=lambda x: x[0])
        result.extend(g(df.copy(), leaves, i))
    calc = pd.DataFrame(result, columns=["from", "to", "type"])
    calc["from"] = pd.to_datetime(calc["from"])
    calc["to"] = pd.to_datetime(calc["to"])

    calc["days_between"] = (calc["to"] - calc["from"]).dt.days + 1
    calc.loc[calc["type"] == 0, "*/11"] = (
            calc.loc[calc["type"] == 0, "days_between"] / 11
    )
    calc.loc[calc["type"] == 0, "*/11"] = calc.loc[calc["type"] == 0, "*/11"].apply(
        lambda x: int(round(x))
    )
    calc.loc[calc["type"] == 0, "*/18"] = (
            calc.loc[calc["type"] == 0, "days_between"] / 18
    )
    calc.loc[calc["type"] == 0, "*/18"] = calc.loc[calc["type"] == 0, "*/18"].apply(
        lambda x: int(round(x))
    )
    calc["*/11-*/18"] = calc["*/11"] - calc["*/18"]
    calc["vl_prevented"] = calc["to"].apply(
        lambda x: calc_vl_prevented_total(x.year, id, cursor) if x == datetime.datetime(x.year, 6, 30) else '-')
    final = pd.DataFrame()
    final['year'] = calc['from'].dt.year
    final["year"] = final["year"].apply(lambda x: f'{x}-{x + 1}')
    final.drop_duplicates(subset=['year'], inplace=True)
    final.reset_index(drop=True, inplace=True)
    final["vl_prevented"] = final["year"].apply(lambda x: calc_vl_prevented_total(int(x[-4:]), id, cursor))
    total = 0
    total_list = []
    for i in range(len(calc)):
        if calc.at[i, 'type'] == 0:
            total += calc.at[i, '*/11-*/18']
            # total_list.append(total)

        else:
            if calc.at[i, 'type'] in ['el', 'lop']:
                total -= calc.at[i, 'days_between']
        calc.at[i, 'total'] = total
        total_list.append(total)
        if calc.at[i, 'vl_prevented'] != '-':
            total += calc.at[i, 'vl_prevented']
            total_list.append(total)
    # print(total_list)
    # print(final)
    # calc = calc.fillna(0)
    calc = calc.fillna('')
    return calc, total_list


def generate_excel(data, total, id):
    if not os.path.exists(dept):
        os.makedirs(dept)
    # print(len(total))
    workbook = xlsxwriter.Workbook(f'{dept}/{id}-{name.strip().replace(" ", "")}.xlsx')
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black'})
    bold_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black'})
    leave_format = workbook.add_format(
        {'bold': True, 'bg_color': '#FFFF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    details_rows = 3
    worksheet.write(0, 0, "Name", cell_format)
    worksheet.write(0, 1, name, cell_format)
    worksheet.write(1, 0, "Date of Joining", cell_format)
    worksheet.write(1, 1, doj.strftime("%d-%m-%Y"), cell_format)
    worksheet.write(2, 0, "Campus", cell_format)
    worksheet.write(2, 1, "Anna University Regional Campus - Tirunelveli", cell_format)
    headers = ["Type of Leave", '', '', '', '*/11', '*/18', '*/11-*/18', 'Total']

    worksheet.write_row(details_rows, 0, headers, bold_format)
    cell_format.set_bold(False)
    worksheet.set_default_row(20)
    worksheet.set_column(0, 0, 15)
    worksheet.set_column(0, 1, 15)
    worksheet.set_column(0, 2, 15)
    # Assuming 'data' is your DataFrame and 'worksheet' is your Excel worksheet

    current_row = 0
    vac_added_count = 0
    current_year = doj.year
    vac_year_added = []
    while current_row < len(data):
        # print(f"Current 'to' date: {data['to'].iloc[current_row]}")
        try:
            if data['from'].iloc[current_row].strftime("%m-%d") == "07-01":
                current_year = data['from'].iloc[current_row].year
                if data.at[current_row, 'type'] != 0:
                    row = [data.at[current_row, 'type'].upper(), data.at[current_row, 'from'].strftime("%d-%m-%Y"),
                           data.at[current_row, 'to'].strftime("%d-%m-%Y"), data.at[current_row, 'days_between'], '',
                           '', data.at[current_row, 'days_between']]
                    worksheet.write_row(current_row + vac_added_count + details_rows + 1, 0, row, leave_format)
                    current_row += 1
                else:
                    row = [data.at[current_row, 'from'].strftime("%d-%m-%Y"),
                           data.at[current_row, 'to'].strftime("%d-%m-%Y"), '', data.at[current_row, 'days_between'],
                           data.at[current_row, '*/11'], data.at[current_row, '*/18'],
                           data.at[current_row, '*/11-*/18']]

                    worksheet.write_row(current_row + vac_added_count + details_rows + 1, 0, row, cell_format)

                    current_row += 1

            while current_row < len(data) and data['from'].iloc[current_row].strftime("%m-%d") != "07-01":
                # print(f"Current 'from' date: {data['from'].iloc[current_row].strftime('%m-%d')}")

                if data.at[current_row, 'type'] == 0:
                    # print("Type 0")
                    # Writing specific data to the worksheet for type 0
                    row = [data.at[current_row, 'from'].strftime("%d-%m-%Y"),
                           data.at[current_row, 'to'].strftime("%d-%m-%Y"), '', data.at[current_row, 'days_between'],
                           data.at[current_row, '*/11'], data.at[current_row, '*/18'],
                           data.at[current_row, '*/11-*/18']]
                    worksheet.write_row(current_row + vac_added_count + details_rows + 1, 0, row, cell_format)
                    current_row += 1
                else:
                    # print("Other Type")
                    # Writing different data to the worksheet for other types
                    row = [data.at[current_row, 'type'].upper(), data.at[current_row, 'from'].strftime("%d-%m-%Y"),
                           data.at[current_row, 'to'].strftime("%d-%m-%Y"), data.at[current_row, 'days_between'], '',
                           '', data.at[current_row, 'days_between']]
                    worksheet.write_row(current_row + vac_added_count + details_rows + 1, 0, row, leave_format)
                    current_row += 1

                if current_row == len(data):
                    # print("Reached end of data")
                    current_row -= 1
                    break
        except IndexError as e:
            print(current_row)
            print(e.with_traceback())

        if current_row < len(data) and data.at[current_row, 'to'].year == 2023:
            print(row)
            print(data.iloc[current_row])
            # Adding 'Add Vacation' row after inner loop completes
        row = ['Add Vacation', f"{current_year}-{current_year + 1}", '',
               data.at[current_row - (1 if current_row != len(data) - 1 else 0), 'vl_prevented'], '', '', '']
        # if not current_year == 2022:
        worksheet.write_row(current_row + vac_added_count + details_rows + (2 if current_row == len(data)-1  else 1), 0, row,
                                bold_format)
        vac_year_added.append(f"{current_year}-{current_year + 1}")
        # if current_row != len(data)-1:
        #     current_row += 1
        vac_added_count += 1
        print(current_year, current_row, len(data))

        if current_row == len(data) - 1:
            break

    for i in range(len(total)):
        worksheet.write(i + 1 + details_rows, 7, total[i], bold_format)
    workbook.close()


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    id = "25005"
    data, total = calculate_leave(id, cursor)
    data.to_csv('data.csv', index=False)
    print(data)
    generate_excel(data, total, id)
