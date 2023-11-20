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
        lambda x: x[0])


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


def get_prevented_dates(from_date, to_date, availed):
    if from_date == "NULL" or to_date == "NULL" or from_date is None or to_date is None:
        return []
    elif availed[0][0] == "NULL":
        return [[from_date, to_date]]
    elif availed[0][0] == from_date and availed[0][1] == to_date:
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
        data[i]["Prevented"] = get_prevented_dates(vac_from, vac_to, availed)
    return pd.DataFrame(data)


def group_to_dict(group):
    group_dict = {
        'from': group['from'].tolist(),
        'to': group['to'].tolist(),
        'Availed_from': group['Availed From'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date() if x != "NULL" else "NULL").tolist(),
        'Availed_to': group['Availed To'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date() if x != "NULL" else "NULL").tolist()
    }
    return group_dict


def get_vl(file, sheet, cursor):
    vl_data = get_vl_data(file, sheet)
    generate_id(vl_data)
    vl_data.drop(['Year', 'Summer / Winter', "From", "To"], axis=1, inplace=True)
    vl_data = vl_data.drop_duplicates()
    vl_data['total_days'] = vl_data.apply(
        lambda x: get_total_days(x['Availed From'], x['Availed To']) if (x["Availed From"] != "NULL" and x[
            "Availed To"] != "NULL") else 0,
        axis=1)

    cursor.execute("SELECT `v_id`, `from`, `to` FROM `general_vacation_details`")
    gen_data = cursor.fetchall()
    gen_data = pd.DataFrame(gen_data, columns=['id', 'from', 'to'])
    gen_data = pd.merge(gen_data, vl_data, on='id', how='inner')
    grouped = gen_data.groupby('id').apply(group_to_dict).to_dict()
    return generate_prevention_details(grouped).to_dict()


if __name__ == "__main__":
    mydb = mysql.connector.connect(host="localhost", port="3306", user="root",
                                   database="facultyleavedb")

    db_cursor = mydb.cursor()
