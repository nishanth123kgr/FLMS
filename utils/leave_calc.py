import mysql.connector
import pandas as pd
import datetime
import ast

def get_vacation_details(cursor):
    cursor.execute("select v_id, `from`, `to` from general_vacation_details")
    vac = cursor.fetchall()
    cursor.reset()

    df = pd.DataFrame(vac, columns=["id", "from", "to"])

    return df

def create_new_id(id):
    first_two_chars = id[:2]
    last_char = 'e' if id[-1] == 's' else 'o'
    return first_two_chars + '_' + last_char

def get_join_semester(joining_date):
    year = str(joining_date.strftime('%Y'))[2:]
    if int(joining_date.strftime('%m')) > 6:
        return year + '_o'
    else:
        return year + '_e'
    
def add_leave_availed(df, id, cursor, type):
    query = 'select `from`, `total` from %s where id=%s' % (type, id)
    cursor.execute(query)
    el = cursor.fetchall()
    cursor.reset()
        
    for i in el:
        for j in range(len(df)):
            if df.at[j, 'working_from'] and df.at[j, 'working_to']:
                if df.at[j, 'working_from'] <= i[0] <= df.at[j, 'working_to']:
                    df.at[j, 'leave_availed'] += i[1]
                    if type == 'el':
                        df.at[j, 'el_availed'] += i[1]
                    break
                elif df.at[j, 'working_from'] <= i[0] and df.at[j, 'working_to'] == None:
                    df.at[j, 'leave_availed'] += i[1]
                    if type == 'el':
                        df.at[j, 'el_availed'] += i[1]
                    break
    return df

def calc_vl_prevented_total(vl_id, staff_id, cursor):
    query = 'select prevented from vl where vac_id=\'%s\' and staff_id=%s' % (vl_id, staff_id)
    cursor.execute(query)
    prevented = cursor.fetchall()
    cursor.reset()
    total_vl = 0
    if len(prevented) > 0:
        # print(prevented)
        # print(prevented[0][0], type(prevented[0][0]))
        prevented = ast.literal_eval(prevented[0][0].decode('utf-8')) if not isinstance(prevented[0][0], str) else eval(prevented[0][0])
        for i in prevented:
            # print(i)
            if i[0] and i[1]:
                from_date = datetime.datetime.strptime(i[0], '%Y-%m-%d')
                to_date = datetime.datetime.strptime(i[1], '%Y-%m-%d')
                total_vl += (to_date - from_date).days + 1
    return total_vl

def get_el_earned(id, cursor):
    df = get_vacation_details(cursor)
    df['new_id'] = df['id'].apply(create_new_id)

    cursor.execute("select doj from staff where id=%s" % id)
    joining_date = cursor.fetchall()[0][0]
    cursor.reset()

    df['sort_key'] = df['new_id'].str[:2].astype(int)*10 + df['new_id'].str[-1].apply(lambda x: 0 if x == 'o' else 1)
    df = df.sort_values('sort_key', ascending=False)
    df = df.drop(columns='sort_key')
    df = df.iloc[::-1]
    df.reset_index(drop=True, inplace=True)
    join_sem = get_join_semester(joining_date)
    join_sem_index = df['new_id'].to_list().index(join_sem)
    df = df.iloc[join_sem_index:]
    df['working_from'] = df['to'].apply(lambda x: None if not x else x + datetime.timedelta(days=1))
    df.reset_index(drop=True, inplace=True)

    df['working_from'] = df['working_from'].shift(1)
    df.at[0, 'working_from'] = joining_date
    # df = df[:-1]
    df['working_to'] = df['from'].apply(lambda x: None if not x else x - datetime.timedelta(days=1))
    df.reset_index(drop=True, inplace=True)
    
    vl_None_index = df['working_from'].values.tolist().index(None)
    df.at[vl_None_index, 'working_from'] = df.at[vl_None_index-1, 'working_from']
    df.drop(columns=['from', 'to'], inplace=True)
    


    # Probation

    cursor.execute("select probation from staff where id=%s" % id)
    probation = cursor.fetchall()
    cursor.reset()
    if len(probation) > 0:
        probation = probation[0][0]

    df_dict = df.T.to_dict()
    prob_sem_ind = 0
    for i in df_dict:
        if df_dict[i]['working_from'] <= probation <= df_dict[i]['working_to']:
            prob_sem_ind = i
            break
    
    df.loc[len(df)] = ''
    df.iloc[prob_sem_ind+1:] = df.iloc[prob_sem_ind+1:].shift(periods=1)
    df.loc[prob_sem_ind+1] = [df.loc[prob_sem_ind]['id'], df.loc[prob_sem_ind]['new_id'], probation+datetime.timedelta(days=1), df.loc[prob_sem_ind]['working_to']]
    df.at[prob_sem_ind, 'working_to'] = probation


    # Probation ends

    df['total_working_days'] = df['working_to'] - df['working_from']
    df['total_working_days'] = df['total_working_days'].apply(lambda x: int(x.days + 1) if isinstance(x, datetime.timedelta) else None)
   
    df['leave_availed'] = 0
    df['el_availed'] = 0
    df = add_leave_availed(df, id, cursor, 'el')
    df = add_leave_availed(df, id, cursor, 'ml')
    df = add_leave_availed(df, id, cursor, 'mtl')
    df = add_leave_availed(df, id, cursor, 'lop')
    
    

    

    df['vl_prevented_total'] = df['id'].apply(lambda x: calc_vl_prevented_total(x, id, cursor))
    
    df['total'] = df['total_working_days'] - df['leave_availed'] 
    df['*/11'] = df.apply(lambda row: round(row['total'] / 11) if (pd.notna(row['total']) and row['working_from'] >= probation) else (round(row['total'] / 22) if pd.notna(row['total']) else None), axis=1)    
    df['*/18'] = df.apply(lambda row: round(row['total'] / 18) if (pd.notna(row['total']) and row['working_from'] >= probation) else (round(row['total'] / 36) if pd.notna(row['total']) else None), axis=1)    
    df['*/11-*/18'] = df['*/11'] - df['*/18']
    df['vl_p/3'] = df['vl_prevented_total'].apply(lambda x: round(x / 3) if pd.notna(x) else None)
    df['final_total'] = df['*/11-*/18'] + df['vl_p/3'] - df['el_availed']
    df['sum_total'] = 0
    sum = 0
    for i in range(len(df)):
        sum+=df.at[i, 'final_total']
        df.at[i, 'sum_total'] = sum

    df.dropna(inplace=True)
    df.rename(columns={'new_id': 'sem'}, inplace=True)

    df_before_probation = df.iloc[:prob_sem_ind+1].copy()
    df_after_probation = df.iloc[prob_sem_ind+1:].copy()
    df_after_probation.reset_index(drop=True, inplace=True)
    df_before_probation.reset_index(drop=True, inplace=True)
    df_before_probation.rename(columns={'*/11': '*/22', '*/18': '*/36', '*/11-*/18':'*/22-*/36'}, inplace=True)

    # print("Before probation:\n")
    # print(df_before_probation)

    # print("\nAfter probation:\n")
    # print(df_after_probation)

    return df_before_probation, df_after_probation


if __name__ == "__main__":
    id = '22019'
    db = mysql.connector.connect(host="localhost", port="3306", user="root", database="facultyleavedb")
    cursor = db.cursor()
    bef, aft = get_el_earned(id, cursor)
    print(bef)
    print(aft)
    

    

    # print('\nTotal EL earned:', df['final_total'].sum())
