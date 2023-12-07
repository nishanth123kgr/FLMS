import datetime

import pandas as pd
from from_csv.el_from_csv import convert_to_desired_format
from from_csv.utils import get_total_days, is_valid_date, extract_year_id
import mysql.connector


def convert_to_usable_format(df):
    top_val = ''
    for i in df.columns:
        col_list = df[i]
        for j in range(len(col_list)):
            col_list.iloc[j] = str(col_list.iloc[j]).strip()
            if col_list.iloc[j] != 'nan':
                top_val = col_list.iloc[j]
                continue
            if top_val != '':
                col_list.iloc[j] = top_val
                continue
    df.columns = ["Year", "Summer / Winter", "From", "To", "Total", "Availed From", "Availed To"]
    df.replace('-', 'NULL', inplace=True)
    return df


def get_vl_data(file, sheet_name):
    df = pd.read_excel(file, sheet_name=sheet_name)
    df = df.iloc[10:, :7]
    df = df.reset_index(drop=True)
    df = convert_to_usable_format(df)
    df['Summer / Winter'] = df['Summer / Winter'].apply(lambda x: x.lower())
    df['From'] = df['From'].apply(lambda x: convert_to_desired_format(x))
    df['To'] = df['To'].apply(lambda x: convert_to_desired_format(x))
    df['Availed From'] = df['Availed From'].apply(lambda x: convert_to_desired_format(x))
    df['Availed To'] = df['Availed To'].apply(lambda x: convert_to_desired_format(x))
    df.drop('Total', axis=1, inplace=True)
    return df


def generate_gen_vac_details(vl_data, cursor):
    gen_data = vl_data.copy().iloc[:, :-2]
    gen_data = gen_data.drop_duplicates()
    gen_data.reset_index(drop=True, inplace=True)
    gen_data['id'] = gen_data['Year'].apply(lambda x: extract_year_id(x)) + gen_data['Summer / Winter'].apply(
        lambda x: x[0])
    gen_data = gen_data.loc[
        gen_data['From'].apply(is_valid_date) & gen_data['To'].apply(is_valid_date)
        ].reset_index(drop=True)
    gen_data['total_days'] = gen_data.apply(
        lambda x: get_total_days(x['From'], x['To']) if (x["From"] != "NULL" and x["To"] != "NULL") else 0,
        axis=1)
    gen_data = gen_data[['id', 'Year', 'Summer / Winter', 'From', 'To', 'total_days']]
    data = gen_data.values.tolist()
    for i in data:
        try:
            cursor.execute(
                "INSERT INTO `general_vacation_details`(`v_id`, `year`, `summer_winter`, `from`, `to`, `total_days`) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (i[0], i[1], i[2], i[3], i[4], i[5]))
            cursor.reset()
        except Exception as e:
            mydb.rollback()
    mydb.commit()


def generate_id(data):
    data['id'] = data['Year'].apply(lambda x: extract_year_id(x)) + data['Summer / Winter'].apply(
        lambda x: ('a' if x[0].lower() == 'w' else 'b') + x[0].upper())


def get_start_date(date_range):
    return date_range[0]


def get_missing_dates(prevented_dates, to_date):
    dates = []

    for i in range(1, len(prevented_dates)):
        nxt = prevented_dates[i - 1][1] + datetime.timedelta(days=1)
        if nxt != prevented_dates[i][0]:
            dates += [[nxt,
                       (prevented_dates[i][0] - datetime.timedelta(
                           days=1))]]

    if prevented_dates[-1][-1] != to_date:
        dates += [[(prevented_dates[-1][-1] + datetime.timedelta(days=1)),
                   to_date]]
    return dates


def g(from_date, to_date, availed_dates):
    if from_date == "NULL" or to_date == "NULL" or from_date is None or to_date is None:
        return []
    elif availed_dates[0][0] == from_date and availed_dates[0][1] == to_date:
        return []
    val = []
    for i in range(len(availed_dates)):
        if availed_dates[i][0] != "NULL":
            val.append(availed_dates[i])
    if from_date.strftime('%d-%m-%Y') == '09-01-2010':
        print(from_date, to_date, availed_dates, val)
    if not val:
        return [[from_date, to_date]]
    result = []
    if val:
        try:
            if val[0][0] != "NULL" and val[0][0].strftime("%d-%m") != from_date.strftime("%d-%m"):
                result.append(
                    [
                        from_date,
                        val[0][0] - datetime.timedelta(days=1),
                    ]
                )
        except Exception as e:
            raise Exception

        for j in range(1, len(val) + 1):
            # result.append(
            #     [
            #         val[j - 1][0],
            #         val[j - 1][1],
            #     ]
            # )

            if j < len(val):
                if ((val[j][0] - datetime.timedelta(days=1)) - (
                        val[j - 1][1] + datetime.timedelta(days=1))).days < 0:
                    continue
                result.append(
                    [
                        val[j - 1][1] + datetime.timedelta(days=1),
                        val[j][0] - datetime.timedelta(days=1),
                    ]
                )
        if val[-1][1] != to_date:
            result.append(
                [
                    val[-1][1] + datetime.timedelta(days=1),
                    to_date,
                ]
            )
    else:
        result.append(
            [
                from_date,
                to_date,
            ]
        )
    return result


def get_prevented_dates(from_date, to_date, availed):
    if from_date == "NULL" or to_date == "NULL" or from_date is None or to_date is None:
        return []

    prevented = []
    total = []
    for (index, avail) in enumerate(availed):
        avail_from, avail_to = avail
        if avail_from == from_date:
            if len(availed) == 1:
                prevented.append([(avail_to + datetime.timedelta(days=1)),
                                  to_date])

            else:
                prevented.append([(avail_to + datetime.timedelta(days=1)),
                                  (availed[availed.index((avail_from, avail_to)) + 1][0] - datetime.timedelta(
                                      days=1))])
        else:
            if index == len(availed) - 1:
                if len(availed) == 1:
                    prevented.append([from_date,
                                      (avail_from - datetime.timedelta(days=1))])
                elif avail_to != to_date:
                    prevented.append([(avail_to + datetime.timedelta(days=1)),
                                      to_date])
                else:
                    prevented.append([(availed[index - 1][1] + datetime.timedelta(days=1)),
                                      (avail_from - datetime.timedelta(days=1))])
            elif index == 0:
                prevented.append([from_date,
                                  (avail_from - datetime.timedelta(days=1))])
            else:
                prevented.append([(avail_to + datetime.timedelta(days=1)),
                                  (availed[index + 1][0] - datetime.timedelta(days=1))])
        total += [[avail_from, avail_to]]
    total += prevented
    # Sort the date ranges based on the start date
    total = set(map(tuple, total))
    total = sorted(total, key=get_start_date)
    prevented += get_missing_dates(total, to_date)
    prevented = list(set(map(tuple, prevented)))
    return sorted(prevented, key=get_start_date)


def generate_prevention_details(data):
    for i in data:
        vac_from = data[i]["from"][0]
        vac_to = data[i]["to"][0]
        availed = list(zip(data[i]["Availed_from"], data[i]["Availed_to"]))
        data[i]["Prevented"] = g(vac_from, vac_to, availed)
    return pd.DataFrame(data)


def group_to_dict(group):
    group_dict = {
        'from': group['from'].tolist(),
        'to': group['to'].tolist(),
        'Availed_from': group['Availed From'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date() if x != "NULL" else "NULL").tolist(),
        'Availed_to': group['Availed To'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date() if x != "NULL" else "NULL").tolist(),
        'others': group['others'].tolist()
    }
    return group_dict


def get_other_leaves(id, type, cursor):
    cursor.execute(
        f"SELECT DISTINCT"
        f" a.`from` AS a_from, a.`to` AS a_to, v.v_id, v.`from` AS v_from, v.`to` AS v_to "
        f"FROM `{type}` a, `general_vacation_details` v "
        f"WHERE ((a.`from` BETWEEN v.`from` AND v.`to`)"
        f"AND (a.`to` BETWEEN v.`from` AND v.`to`))"
        f"and a.id={id}")
    leave_data = cursor.fetchall()
    cursor.reset()
    cursor.execute(
        f"SELECT DISTINCT"
        f" a.`from` AS a_from, a.`to` AS a_to, v.v_id, v.`from` AS v_from, v.`to` AS v_to "
        f"FROM `{type}` a, `general_vacation_details` v "
        f"WHERE v.`from` >= a.`from` AND a.`to` >= v.`to` and a.id={id}")
    leave_data += cursor.fetchall()
    cursor.reset()
    cursor.execute(
        f"SELECT DISTINCT"
        f" a.`from` AS a_from, a.`to` AS a_to, v.v_id, v.`from` AS v_from, v.`to` AS v_to "
        f"FROM `{type}` a, `general_vacation_details` v "
        f"WHERE (a.`from` BETWEEN v.`from` AND v.`to`)"
        f"and a.id={id}")
    leave_data += cursor.fetchall()
    cursor.reset()
    cursor.execute(
        f"SELECT DISTINCT"
        f" a.`from` AS a_from, a.`to` AS a_to, v.v_id, v.`from` AS v_from, v.`to` AS v_to "
        f"FROM `{type}` a, `general_vacation_details` v "
        f"WHERE (a.`to` BETWEEN v.`from` AND v.`to`)"
        f"and a.id={id}")
    leave_data += cursor.fetchall()
    leave_data = list(set(leave_data))
    cursor.reset()

    return leave_data


def insert_other_leavedata(id, vl_data, cursor):
    for leave_type in ['el', 'ml', 'mtl', 'lop', 'sl', 'eol']:
        others = [[from_date, to_date, leave_id, leave_type, v_from, v_to] for
                  from_date, to_date, leave_id, v_from, v_to in
                  get_other_leaves(id, leave_type, cursor)]
        if others:
            print(others)
            for i in others:
                l_from = None
                l_to = None
                if i[0] <= i[4] and i[1] >= i[5]:
                    l_from = i[4]
                    l_to = i[5]
                elif i[0] <= i[4] and i[1] <= i[5]:
                    l_from = i[4]
                    l_to = i[1]
                elif i[0] >= i[4] and i[1] >= i[5]:
                    l_from = i[0]
                    l_to = i[5]
                elif i[0] >= i[4] and i[1] <= i[5]:
                    l_from = i[0]
                    l_to = i[1]
                new_row = {'Availed From': l_from.strftime("%Y-%m-%d"), 'Availed To': l_to.strftime("%Y-%m-%d"),
                           'id': i[2][:-1] + ('a' if i[2][-1] == 'w' else 'b') + i[2][-1].upper(),
                           'others': f'{i[3]}_{id}_{l_from}'}
                new_row = pd.Series(new_row)
                vl_data.loc[len(vl_data)] = new_row
    return vl_data


def reset_data_id(data):
    data['id'] = data['id'].apply(lambda x: x[:-2] + x[-1].lower())
    return data


def get_vl(id, file, sheet, cursor):
    vl_data = get_vl_data(file, sheet)
    generate_id(vl_data)
    vl_data.drop(['Year', 'Summer / Winter', "From", "To"], axis=1, inplace=True)
    vl_data = vl_data.drop_duplicates()
    vl_data.reset_index(drop=True, inplace=True)
    vl_data['others'] = "NULL"
    insert_other_leavedata(id, vl_data, cursor)
    vl_data['total_days'] = vl_data.apply(
        lambda x: get_total_days(x['Availed From'], x['Availed To']) if (x["Availed From"] != "NULL" and x[
            "Availed To"] != "NULL") else 0,
        axis=1)
    cursor.execute("SELECT `v_id`, `from`, `to` FROM `general_vacation_details`")
    gen_data = cursor.fetchall()
    cursor.reset()
    gen_data = pd.DataFrame(gen_data, columns=['id', 'from', 'to'])

    gen_data['id'] = gen_data['id'].apply(
        lambda x: x[:-1] + ('a' if x[-1] == 'w' else 'b') + x[-1].upper())
    gen_data = pd.merge(gen_data, vl_data, on='id', how='inner')

    gen_data = gen_data.sort_values(by=['id', 'Availed From'])
    gen_data.reset_index(drop=True, inplace=True)
    reset_data_id(gen_data)
    print(gen_data)
    grouped = gen_data.groupby('id').apply(group_to_dict).to_dict()
    final = generate_prevention_details(grouped)
    print(final.to_dict())
    return final.to_dict()


if __name__ == "__main__":
    mydb = mysql.connector.connect(host="localhost", port="3306", user="root",
                                   database="facultyleavedb")
    id = '25009'
    db_cursor = mydb.cursor()
    print(get_vl(id, '../25009-Rajakumar  - 05.09.2023.xlsx', "VL", db_cursor))
