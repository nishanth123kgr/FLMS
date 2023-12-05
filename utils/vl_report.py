import ast
import json
import os
from datetime import datetime

import mysql.connector
import numpy as np
import pandas as pd
import xlsxwriter


def get_vl_details(id, cursor):
    cursor.execute(f"select `vac_id`,  `prevented` from vl where staff_id={id}")
    prevented_details = cursor.fetchall()
    cursor.reset()

    cursor.execute(f"select `vac_id`, `availed_from`, `availed_to` from vl where staff_id={id}")
    availed_details = cursor.fetchall()
    cursor.reset()

    return prevented_details, availed_details


def parse_json(data):
    for i in range(len(data)):
        data[i] = list(data[i])
        for j in range(1, len(data[i])):
            if data[i][j] is None:
                continue
            if data[i][j] == "NULL":
                data[i][j] = None
                continue
            data[i][j] = ast.literal_eval(data[i][j])

    return data


def split_prevented_from_to(data):
    df_new = []
    for i in range(len(data)):
        for j in range(len(data.at[i, 'Prevented'])):
            df_new.append([data.at[i, 'Year'], data.at[i, 'Prevented'][j][0], data.at[i, 'Prevented'][j][1]])
    return pd.DataFrame(df_new, columns=['Year', 'Prevented From', 'Prevented To'])


def split_availed_from_to(data):
    df_new = []
    for i in range(len(data)):
        if data.at[i, 'Availed From'] is None and data.at[i, 'Availed To'] is None:
            continue
        for from_date, to_date in zip(data.at[i, 'Availed From'], data.at[i, 'Availed To']):
            df_new.append([data.at[i, 'Year'], from_date, to_date])
    return pd.DataFrame(df_new, columns=['Year', 'Availed From', 'Availed To'])


def group_to_dict(group):
    group_dict = {
        "year": group['Year'],
        'from': group['from'],
        'to': group['to'],
    }
    return group_dict


def get_general_details(id, cursor):
    cursor.execute(
        f"select v_id, `from`, `to` from general_vacation_details where v_id in (select vac_id from vl where staff_id={id})")
    df = pd.DataFrame(cursor.fetchall(), columns=['Year', 'from', 'to'])
    cursor.reset()
    return df


def get_year_total(year_id, cursor):
    query = f'select sum(total_days) from general_vacation_details where (v_id="{year_id}s") or (v_id="{year_id}w");'
    cursor.execute(query)
    total = cursor.fetchone()[0]
    cursor.reset()
    return total


def get_other_leaves(id, cursor):
    query = f'select other_leave from vl where staff_id={id}'
    cursor.execute(query)
    other_leave = cursor.fetchall()
    cursor.reset()
    leaves = []
    for leave in other_leave:
        leave = list(filter(lambda x: x != "NULL", eval(leave[0])))
        leaves.extend(leave)
    print(leaves)
    return leaves


def set_other_leaves(id, cursor, data):
    other_leaves = get_other_leaves(id, cursor)
    for i in other_leaves:
        l_type, s_id, from_date = i.split('_')
        data.loc[data["Availed From"] == from_date, "others"] = l_type


def generate_excel(data, id, name, dept, doj, workbook, cursor):
    worksheet = workbook.add_worksheet("VL")
    worksheet.set_column('A:O', 12)
    worksheet.set_default_row(20)
    merge_ranges = [
        (2, 0, 2, 3),
        (2, 4, 2, 14),
        (3, 0, 3, 3),
        (3, 4, 3, 14),
        (4, 0, 4, 3),
        (4, 4, 4, 14),
        (5, 0, 5, 3),
        (5, 4, 5, 14),
        (6, 0, 6, 3),
        (6, 4, 6, 14),
        (7, 0, 7, 14),
        (8, 0, 8, 4),
        (8, 5, 8, 14)

    ]
    cell_format_center = workbook.add_format({
        'align': 'center',  # Center alignment
        'text_wrap': True,  # Wrap text
        'valign': 'vcenter',  # Center vertically
        'border': 1
    })
    cell_format_left = workbook.add_format({
        'align': 'left',  # Center alignment
        'text_wrap': True,  # Wrap text
        'valign': 'vcenter',  # Center vertically
        'border': 1
    })
    year_format = {
        0: workbook.add_format({'align': 'center',  # Center alignment
                                'text_wrap': True,  # Wrap text
                                'valign': 'vcenter',  # Center vertically
                                'border': 1,
                                'bg_color': '#ffff00'}),
        1: workbook.add_format({
            'align': 'center',  # Center alignment
            'text_wrap': True,  # Wrap text
            'valign': 'vcenter',  # Center vertically
            'border': 1,
            'bg_color': '#90EE90'
        })
    }

    # Perform the defined merges
    worksheet.merge_range(*(0, 0, 0, 14), 'Annexure -II', cell_format_center)
    worksheet.merge_range(*(1, 0, 1, 14), 'Anna University chennai', cell_format_center)
    worksheet.merge_range(*merge_ranges[0], 'Name', cell_format_left)
    worksheet.merge_range(*merge_ranges[1], name, cell_format_left)
    worksheet.merge_range(*merge_ranges[2], 'Designation', cell_format_left)
    worksheet.merge_range(*merge_ranges[3], '', cell_format_left)
    worksheet.merge_range(*merge_ranges[4], 'Department', cell_format_left)
    worksheet.merge_range(*merge_ranges[5], dept, cell_format_left)
    worksheet.merge_range(*merge_ranges[6], 'Date of joining in service', cell_format_left)
    worksheet.merge_range(*merge_ranges[7], doj.strftime('%d-%m-%Y'), cell_format_left)
    worksheet.merge_range(*merge_ranges[8], 'Campus', cell_format_left)
    worksheet.merge_range(*merge_ranges[9], 'ANNA UNIVERSITY REGIONAL CAMPUS   -   TIRUNELVELI', cell_format_left)
    worksheet.merge_range(*merge_ranges[10], 'Details of Vacation', cell_format_center)

    worksheet.merge_range("B9:O9", "Vacation", cell_format_center)
    worksheet.merge_range("A9:A11", "Year", cell_format_center)
    worksheet.merge_range("B10:F10", "Period of Vacation", cell_format_center)
    worksheet.merge_range("G10:K10", "Vacation Availed", cell_format_center)
    worksheet.merge_range("L10:O10", "Vacation Prevention", cell_format_center)
    worksheet.write("B11", "Semester", cell_format_center)
    worksheet.write("C11", "From", cell_format_center)
    worksheet.write("D11", "To", cell_format_center)
    worksheet.write("E11", "Total", cell_format_center)
    worksheet.write("F11", "Year Total", cell_format_center)
    worksheet.write("G11", "From", cell_format_center)
    worksheet.write("H11", "To", cell_format_center)
    worksheet.write("I11", "Remarks", cell_format_center)
    worksheet.write("J11", "Total", cell_format_center)
    worksheet.write("K11", "Year Total", cell_format_center)
    worksheet.write("L11", "From", cell_format_center)
    worksheet.write("M11", "To", cell_format_center)
    worksheet.write("N11", "Total", cell_format_center)
    worksheet.write("O11", "Year Total", cell_format_center)

    row = 12
    sums = {"row": 0, "avail": 0, "preven": 0, "period": 0}
    year_type = 0
    for year, values in data.items():
        from_date = values[0]['from']
        to_date = values[0]['to']
        if year[-1] == 'W' or row == 12:
            sums["row"] = row
        props = {
            "row": row,
            "avail": 0,
            "preven": 0
        }
        for items in values:
            avail_sum = (datetime.strptime(items['Availed To'], "%Y-%m-%d") - datetime.strptime(items['Availed From'],
                                                                                                "%Y-%m-%d")).days + 1 if \
                items['Availed From'] not in ['', 'NULL'] and items['Availed To'] not in ['', 'NULL'] else 0
            preven_sum = (datetime.strptime(items['Prevented To'], "%Y-%m-%d") - datetime.strptime(
                items['Prevented From'],
                "%Y-%m-%d")).days + 1 if \
                items['Prevented From'] not in ['', 'NULL'] and items['Prevented To'] not in ['', 'NULL'] else 0
            props["avail"] += avail_sum
            props["preven"] += preven_sum
            availed_from = datetime.strptime(items['Availed From'], "%Y-%m-%d").strftime("%d-%m-%Y") if items[
                                                                                                            'Availed From'] not in [
                                                                                                            '',
                                                                                                            'NULL'] else '-'
            availed_to = datetime.strptime(items['Availed To'], "%Y-%m-%d").strftime("%d-%m-%Y") if items[
                                                                                                        'Availed To'] not in [
                                                                                                        '',
                                                                                                        'NULL'] else '-'
            prevented_from = datetime.strptime(items['Prevented From'], "%Y-%m-%d").strftime("%d-%m-%Y") if items[
                                                                                                                'Prevented From'] not in [
                                                                                                                '',
                                                                                                                'NULL'] else '-'
            prevented_to = datetime.strptime(items['Prevented To'], "%Y-%m-%d").strftime("%d-%m-%Y") if items[
                                                                                                            'Prevented To'] not in [
                                                                                                            '',
                                                                                                            'NULL'] else '-'
            worksheet.write(f"G{row}", availed_from,
                            year_format[year_type])
            worksheet.write(f"H{row}", availed_to,
                            year_format[year_type])
            worksheet.write(f"I{row}", f"Availed {items['others'].upper()}" if items['others'] else '-', year_format[year_type])
            worksheet.write(f"J{row}", avail_sum if avail_sum else '-', year_format[year_type])
            worksheet.write(f"L{row}", prevented_from,
                            year_format[year_type])
            worksheet.write(f"M{row}", prevented_to,
                            year_format[year_type])
            worksheet.write(f"N{row}", preven_sum if preven_sum else '-', year_format[year_type])

            row += 1
        sums["avail"] += props["avail"]
        sums["preven"] += props["preven"]
        if year[-1] == 'S' or list(data.items())[-1] == (year, values):
            if sums["row"] == row - 1:
                worksheet.write(f'K{sums["row"]}', sums["avail"], year_format[year_type])
                worksheet.write(f'O{sums["row"]}', sums["preven"], year_format[year_type])
                worksheet.write(f'A{sums["row"]}', f'20{year[:2]}-20{year[3:5]}', year_format[year_type])
                worksheet.write(f'F{sums["row"]}', get_year_total(year[:-2], cursor), year_format[year_type])
            else:
                worksheet.merge_range(f'K{sums["row"]}:K{row - 1}', sums["avail"], year_format[year_type])
                worksheet.merge_range(f'O{sums["row"]}:O{row - 1}', sums["preven"], year_format[year_type])
                worksheet.merge_range(f'A{sums["row"]}:A{row - 1}', f'20{year[:2]}-20{year[3:5]}',
                                      year_format[year_type])
                worksheet.merge_range(f'F{sums["row"]}:F{row - 1}', get_year_total(year[:-2], cursor),
                                      year_format[year_type])
            sums = {"row": 0, "avail": 0, "preven": 0}

        from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else '-'
        to_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else '-'
        if props["row"] == row - 1:
            worksheet.write(f"C{props['row']}", from_date.strftime("%d-%m-%Y") if from_date != '-' else '-',
                            year_format[year_type])
            worksheet.write(f"D{props['row']}", to_date.strftime("%d-%m-%Y") if to_date != '-' else '-',
                            year_format[year_type])
            if from_date != '-' and to_date != '-':
                worksheet.write(f"E{props['row']}", (to_date - from_date).days + 1, year_format[year_type])
            else:
                worksheet.write(f"E{props['row']}", '-', year_format[year_type])
        else:
            worksheet.merge_range(f"C{props['row']}:C{row - 1}",
                                  from_date.strftime("%d-%m-%Y") if from_date != '-' else '-',
                                  year_format[year_type])
            worksheet.merge_range(f"D{props['row']}:D{row - 1}",
                                  to_date.strftime("%d-%m-%Y") if to_date != '-' else '-',
                                  year_format[year_type])
            if from_date != '-' and to_date != '-':
                worksheet.merge_range(f"E{props['row']}:E{row - 1}",
                                      (to_date - from_date).days + 1 if from_date else '-',
                                      year_format[year_type])
            else:
                worksheet.merge_range(f"E{props['row']}:E{row - 1}",
                                      '-',
                                      year_format[year_type])
        if year[-1] == 'W':
            if props['row'] == row - 1:
                worksheet.write(f"B{props['row']}", 'Winter', year_format[year_type])
            else:
                worksheet.merge_range(f"B{props['row']}:B{row - 1}", "Winter", year_format[year_type])
        else:
            if props['row'] == row - 1:
                worksheet.write(f"B{props['row']}", 'Summer', year_format[year_type])
            else:
                worksheet.merge_range(f"B{props['row']}:B{row - 1}", "Summer", year_format[year_type])
            year_type = 0 if year_type == 1 else 1


def convert_data(data):
    data = data.fillna("")
    data = data.T.to_dict()
    converted_data = {}
    for key, value in data.items():
        year_key = key[0]
        if year_key not in converted_data:
            converted_data[year_key] = []
        if value['from'] is not None and value['from']:
            value['from'] = value['from'].strftime("%Y-%m-%d")
        if value['from'] is not None and value['from']:
            value['to'] = value['to'].strftime("%Y-%m-%d")
        converted_data[year_key].append(value)
    return converted_data


def get_staff_details(id, cursor):
    cursor.execute(f"select `name`, `department`, `doj` from staff where id={id}")
    name, dept, doj = cursor.fetchone()
    return name, dept, doj


def generate_vl(id, cursor, workbook):
    name, dept, doj = get_staff_details(id, cursor)
    prevention, availed = get_vl_details(id, cursor)
    general_details = get_general_details(id, cursor)
    general_details["Year"] = general_details["Year"].apply(
        lambda x: x[:-1] + f"{'w' if x[-1] == 's' else 'a'}{x[-1].upper()}")
    prevention = pd.DataFrame(parse_json(prevention), columns=['Year', 'Prevented'])
    prevention["Year"] = prevention["Year"].apply(lambda x: x[:-1] + f"{'w' if x[-1] == 's' else 'a'}{x[-1].upper()}")
    availed = pd.DataFrame(parse_json(availed), columns=['Year', 'Availed From', 'Availed To'])
    availed["Year"] = availed["Year"].apply(lambda x: x[:-1] + f"{'w' if x[-1] == 's' else 'a'}{x[-1].upper()}")
    prevention = split_prevented_from_to(prevention).groupby('Year').apply(lambda x: x.reset_index(drop=True))
    prevention.drop(['Year'], axis=1, inplace=True)
    availed = split_availed_from_to(availed).groupby('Year').apply(lambda x: x.reset_index(drop=True))
    availed.drop(['Year'], axis=1, inplace=True)
    general_details = general_details.groupby('Year').apply(lambda x: x.reset_index(drop=True))
    general_details.drop(['Year'], axis=1, inplace=True)

    new1 = pd.concat([general_details, availed, prevention], axis=1, join='outer').sort_index()
    new1['others'] = np.nan
    set_other_leaves(id, cursor, new1)
    print(new1)
    data = convert_data(new1)
    print(data)
    generate_excel(data, id, name, dept, doj, workbook, cursor)


if __name__ == "__main__":
    id = 22007
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    workbook = xlsxwriter.Workbook(f'VL/{id}_VL.xlsx')
    generate_vl(id, cursor, workbook)
    workbook.close()
    cursor.close()
