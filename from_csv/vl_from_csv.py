import pandas as pd
from from_csv.el_from_csv import convert_to_desired_format


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


def get_vl(file, sheet_name):
    df = pd.read_excel(file, sheet_name=sheet_name)
    df = df.iloc[10:, :7]
    df = df.reset_index(drop=True)
    # gen_df = df.copy().iloc[:, :-3]
    # gen_df.dropna(inplace=True)
    # gen_df = gen_df.reset_index(drop=True)
    # gen_df.columns = ["Year", "Summer / Winter", "From", "To"]
    # gen_df["From"] = gen_df["From"].apply(lambda x: convert_to_desired_format(x))
    # gen_df["To"] = gen_df["To"].apply(lambda x: convert_to_desired_format(x))
    # print(gen_df)
    df = convert_to_usable_format(df)
    df['From'] = df['From'].apply(lambda x: convert_to_desired_format(x))
    df['To'] = df['To'].apply(lambda x: convert_to_desired_format(x))
    df['Availed From'] = df['Availed From'].apply(lambda x: convert_to_desired_format(x))
    df['Availed To'] = df['Availed To'].apply(lambda x: convert_to_desired_format(x))
    df.drop('Total', axis=1, inplace=True)
    return df


if __name__ == "__main__":
    vl_data = get_vl("../02-Dr.Golden-FINAL24.08.2023.xlsx", 'VL')
    gen_data = vl_data.copy().iloc[:, :-2]
    gen_data = gen_data.drop_duplicates()
    gen_data.reset_index(drop=True, inplace=True)
    gen_data['id'] = gen_data['Year'].apply(lambda x: x.split('-')[0])+"hi"
    print(gen_data)
    # print(vl_data.loc[:, 'From':'Availed To'])
