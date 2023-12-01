import pandas as pd
from datetime import datetime
import re


def convert_to_desired_format(date_str):
    if isinstance(date_str, datetime):
        return date_str.strftime("%Y-%m-%d")
    if "." in date_str:
        input_date_format = "%d.%m.%Y"
    elif ":" in date_str:
        input_date_format = "%Y-%m-%d %H:%M:%S"
    elif "-" in date_str:
        input_date_format = "%d-%m-%Y"
    elif "/" in date_str:
        input_date_format = "%d/%m/%Y"
    else:
        input_date_format = "%d.%m.%Y"
    try:
        parsed_date = datetime.strptime(date_str, input_date_format)
        converted_date_str = parsed_date.strftime("%Y-%m-%d")
        return converted_date_str
    except ValueError as e:
        return date_str


def is_valid_date_format(date_string, format_string="%Y-%m-%d"):
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False


def separate_prefix_suffix(from_date, to_date, date_str):
    try:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return
    date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{2}|\d{2}-\d{2}-\d{4}|[0-9]{2}.[0-9]{2}.[0-9]{4}'

    # Find all dates in the string
    dates = re.findall(date_pattern, date_str)
    dates = [convert_to_desired_format(date) for date in dates]
    from_prefix, to_prefix, from_suffix, to_suffix = "", "", "", ""

    for date in dates:
        date_format = "%Y-%m-%d" if "-" in date else "%d.%m.%Y" if "." in date else "%d/%m/%Y" if "/" in date else "%Y-%m-%d"
        if is_valid_date_format(date, date_format):
            pass
        else:
            dates.remove(date)
    if dates:
        dates.sort(key=lambda date: datetime.strptime(date, date_format))
        for date in dates:
            date = datetime.strptime(date, date_format)
            if date < from_date:
                if not from_prefix:
                    from_prefix = date.strftime(date_format)
                else:
                    if datetime.strptime(from_prefix, date_format) < date:
                        to_prefix = date.strftime(date_format)
            else:
                if not from_suffix:
                    from_suffix = date.strftime(date_format)
                else:
                    if datetime.strptime(from_suffix, date_format) < date:
                        to_suffix = date.strftime(date_format)
    prefix_suffix = tuple(map(lambda x: "NULL" if not x else x, [from_prefix, to_prefix, from_suffix, to_suffix]))
    return prefix_suffix


def remove_extra(date_str):
    if '(' in date_str:
        date_str = date_str.split('(')[0].strip()
    return date_str


def get_el(file, sheet_name):
    # Load Excel data into a DataFrame
    df = pd.read_excel(file, sheet_name=sheet_name)  # -1 selects the last sheet
    df.columns = df.iloc[6].fillna("_").tolist()
    df = df.iloc[9:, :5]
    df = df.reset_index(drop=True)

    data = []
    for i, row in df.iterrows():
        row = list(map(str, row.fillna("NULL").tolist()))
        row = list(map(str.strip, row))
        print(row)
        if not set(row).issubset({"NULL", "-"}):
            if row[0] != "NULL" and row[1] != "NULL" and row[0] != "-" and row[1] != "-":
                # row[-1] = str(row[-1]).removesuffix("*") if row[-1] != "NULL" else row[-1]
                row[-1] = str(row[-1])[:-1] if row[-1] != "NULL" else row[-1]
                row[0] = remove_extra(row[0])
                row[1] = remove_extra(row[1])
                row[3] = remove_extra(row[3])
                row = [convert_to_desired_format(date_str) for date_str in row]
                row[2] = separate_prefix_suffix(row[0], row[1], row[2])
                data.append(row)

    return data


if __name__ == "__main__":
    print(get_el("../Dr.BJ-07.09.2023.xlsx", "EL"))
