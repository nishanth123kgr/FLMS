import datetime
import re


def get_total_days(from_date, to_date):
    date_format = "%Y-%m-%d" if "-" in from_date else "%d.%m.%Y" if "." in from_date else "%d/%m/%Y"
    from_date = datetime.datetime.strptime(from_date, date_format)
    to_date = datetime.datetime.strptime(to_date, date_format)
    return (to_date - from_date).days + 1


def is_valid_date(date_string):
    if date_string == "NULL":
        return True
    date_pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
    return bool(re.match(date_pattern, date_string))


def extract_year_id(year_str):
    year = []
    for i in year_str.split('-'):
        if len(i) == 4:
            year.append(i[-2:])
        else:
            year.append(i)
    return '-'.join(year)


def convert_to_date_text(date, date_format="%d-%m-%Y"):
    if isinstance(date, str):
        if date == "NULL":
            return date
        return datetime.datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
    elif isinstance(date, datetime.date):
        return date.strftime(date_format)
    elif isinstance(date, list):
        return [convert_to_date_text(item) for item in date]
    elif isinstance(date, tuple):
        return [convert_to_date_text(item) for item in date]
    else:
        return date



if __name__ == "__main__":
    data = {
        '10-11s': {
            'Availed_from': ['NULL'],
            'Availed_to': ['NULL'],
            'Prevented': [['19-05-2011', '01-06-2011']],
            'from': ['19-05-2011'],
            'to': ['01-06-2011']
        }
    }
    for key, value in data.items():
        data[key] = {inner_key: convert_to_date_text(inner_value, "%Y-%m-%d") for inner_key, inner_value in
                    value.items()}

    print(data)
