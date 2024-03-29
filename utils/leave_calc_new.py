import mysql.connector
import pandas as pd
import datetime
import ast
import json
import math
import xlsxwriter
import os
import dateutil.relativedelta

name = ''
doj = ''
dept = ''
leaved = ''


def set_staff_data(cursor, id):
    query = "select doj, name, department, leaved_date from staff where id=%s" % (id)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.reset()
    global name, doj, dept, leaved
    name = data[0][1]
    doj = data[0][0]
    dept = data[0][2]
    leaved = data[0][3]


def leave_availed(cursor, id, type, from_date, to_date):
    query = (
            "SELECT `from`, `to` FROM %s WHERE id = %s AND `from` >= '%s' AND `to` <= '%s';"
            % (type, id, from_date, to_date)
    )
    cursor.execute(query)
    leave_availed = cursor.fetchall()
    print(leave_availed, query)
    cursor.reset()
    # query = (
    #         "SELECT `from`, `to` FROM %s WHERE id = %s AND `from` >= '%s' AND `to` <= '%s';"
    #         % (type, id, from_date, to_date + dateutil.relativedelta.relativedelta(years=1))
    # )
    cursor.execute(query)
    leave_availed1 = cursor.fetchall()
    for i in range(len(leave_availed1)):
        if leave_availed1[i][0] < from_date.date():
            print(leave_availed1[i][0], leave_availed1[i][1], type)
    return [[start, end, type] for start, end in leave_availed]


def g(df, leaves, i):
    result = []
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


def calc_vl_prevented_total(to_date, staff_id, cursor, dt):
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
    from_end = f"{datetime.datetime.now().year - 1}-07-01"
    to_end = f"{datetime.datetime.now().year}-06-30"
    if leaved:
        from_end = f'{leaved.year - 1 if leaved.month < 7 else leaved.year}-07-01'
        to_end = leaved
    from_date_range = pd.date_range(
        start=date_of_join,
        end=from_end,
        freq="AS-JUL",
    ).tolist()
    from_date_range.insert(0, date_of_join)
    date_range = pd.date_range(
        start=f"{date_of_join.year}-06-30",
        end=to_end,
        freq="A-JUN",
    )

    # Filter the date range based on date_of_join
    to_date_range = date_range[date_range > date_of_join]

    if leaved:
        to_date_range = to_date_range.tolist()
        to_date_range.append(leaved)
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
    # print(calc['to'].iloc[-1].strftime("%d-%m-%Y"),calc['to'].iloc[-1].strftime("%d-%m-%Y")== leaved.strftime("%d-%m-%Y"))
    if leaved:
        calc["vl_prevented"] = calc["to"].apply(
            lambda x: calc_vl_prevented_total(x.year, id, cursor, x) if x == datetime.datetime(x.year, 6,
                                                                                               30) or x.strftime(
                "%d-%m-%Y") == (leaved.strftime("%d-%m-%Y") if leaved else False) else '-')
    else:
        calc["vl_prevented"] = calc["to"].apply(
            lambda x: calc_vl_prevented_total(x.year, id, cursor, x) if x == datetime.datetime(x.year, 6,
                                                                                               30) else '-')

    # final = pd.DataFrame()
    # final['year'] = calc['from'].dt.year
    # final["year"] = final["year"].apply(lambda x: f'{x}-{x + 1}')
    # final.drop_duplicates(subset=['year'], inplace=True)
    # final.reset_index(drop=True, inplace=True)
    # final["vl_prevented"] = final["year"].apply(lambda x: calc_vl_prevented_total(int(x[-4:]), id, cursor, x))
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


def generate_excel(data):
    if not os.path.exists(dept):
        os.makedirs(dept)

    file_name = f'{dept}/LeaveRecords.xlsx'

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': 'black'})
    bold_format = workbook.add_format(
        {'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': 'black'})
    leave_format = workbook.add_format(
        {'bold': True, 'bg_color': '#FFFF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,
         'border_color': 'black'})

    details_rows = 0

    headers = ["From", "To", "Type", "Days Between", "*/11", "*/18", "*/11-*/18", "VL Prevented", "Total"]

    worksheet.write_row(details_rows, 0, headers, bold_format)

    for i in range(len(data)):
        row = [
            data.at[i, 'from'].strftime("%Y-%m-%d"),
            data.at[i, 'to'].strftime("%Y-%m-%d"),
            data.at[i, 'type'].upper() if data.at[i, 'type'] != 0 else '0',
            data.at[i, 'days_between'],
            data.at[i, '*/11'] if data.at[i, 'type'] != 0 else '',
            data.at[i, '*/18'] if data.at[i, 'type'] != 0 else '',
            data.at[i, '*/11-*/18'] if data.at[i, 'type'] != 0 else '',
            data.at[i, 'vl_prevented'] if data.at[i, 'type'] != 0 else '',
            data.at[i, 'total']
        ]

        if data.at[i, 'to'].strftime("%m-%d") == "06-30":
            row = ["Vacation Added"] + row[1:]
            worksheet.write_row(details_rows + i + 1, 0, row, bold_format)
            details_rows += 1

        worksheet.write_row(details_rows + i + 1, 0, row, leave_format if data.at[i, 'type'] != 0 else cell_format)

    workbook.close()


def gen_excel(data, id):
    if not os.path.exists(dept):
        os.makedirs(dept)
    workbook = xlsxwriter.Workbook(f'{dept}/{id}-{name.strip().replace(" ", "")}.xlsx')
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black'})
    bold_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black'})
    el_format = workbook.add_format(
        {'bold': True, 'bg_color': '#FFFF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    ml_format = workbook.add_format(
        {'bold': True, 'bg_color': '#00FF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    mtl_format = workbook.add_format(
        {'bold': True, 'bg_color': '#009eff', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    lop_format = workbook.add_format(
        {'bold': True, 'bg_color': '#ff00fe', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    leave_format = {
        "el": el_format,
        "ml": ml_format,
        "mtl": mtl_format,
        "lop": lop_format
    }
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
    worksheet.set_default_row(25)
    worksheet.set_column(0, 0, 15)
    worksheet.set_column(0, 1, 15)
    worksheet.set_column(0, 2, 15)
    data["*/11"] = data["*/11"].apply(lambda x: int(x) if x != '' else x)
    data["*/18"] = data["*/18"].apply(lambda x: int(x) if x != '' else x)
    data["*/11-*/18"] = data["*/11-*/18"].apply(lambda x: int(x) if x != '' else x)
    data["total"] = data["total"].apply(lambda x: int(x) if x != '' else x)
    rows = []
    for i in range(len(data)):
        row_values = data.iloc[i].copy().tolist()
        rows.append(row_values)
        if data.at[i, 'to'].strftime("%d-%m") == '30-06' or i == len(data) - 1:
            rows.append(["Add Vacation", f'{data["to"].iloc[i].year - 1}-{data["to"].iloc[i].year}', '',
                         data.at[i, 'vl_prevented'],
                         '', '', '', '', data.at[i, 'vl_prevented'] + data.at[i, 'total']])
    data = pd.DataFrame(rows, columns=["from", "to", "type", "days", "/11", "/18", "/11-/18", "vl", "total"])
    data = data.drop('vl', axis=1)
    for i in range(len(data)):
        row = data.iloc[i].tolist()
        if row[2] == 0:
            worksheet.write_row(i + 4, 0,
                                [row[0].strftime("%d-%m-%Y"), row[1].strftime("%d-%m-%Y")] + [''] + row[3:],
                                cell_format)
        elif row[2] in ['el', 'ml', 'mtl', 'lop']:
            worksheet.write_row(i + 4, 0,
                                [row[2].upper(), row[0].strftime("%d-%m-%Y"), row[1].strftime("%d-%m-%Y")] + row[3:],
                                leave_format[row[2]])
        else:
            worksheet.write_row(i + 4, 0, row, bold_format)
    workbook.close()


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    # ids =
    # ids = [30002, 20003, 30003, 45000, 45001]
    # ids = [24001, 24003]
    # ids = [26001, 55555]
    ids = [13333] + [12222, 12223, 12224, 25001, 25005, 25007, 25009, 25010, 25012, 25013, 25019, 25030, 13331, 13332,
                     13333, 27002] + [30002, 20003, 30003, 45000, 45001] + [26001, 55555] + [10001, 21002, 21003, 21010, 66661]
    print(ids)
    for i in ids:
        data, total = calculate_leave(i, cursor)
        gen_excel(data, i)
