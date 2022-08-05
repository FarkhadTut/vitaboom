from tkinter import image_names
import requests
import os 
from database.connector import con
import pandas as pd
from datetime import datetime, timedelta
from numpy import isnan
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils import get_column_letter
import glob
import os 



media_path = os.path.join(os.getcwd(), 'media')


def intersection(lst1, lst2):
    l = list(set(lst1) & set(lst2))
    if len(l) == 0:
        return False
    return True 

def generate_report(record_df):
    temp_out = pd.DataFrame()
    date = record_df['date'].values[0]
    uuid = record_df['record_id'].values[0]
    for idx in record_df.index:
        answer_id = record_df['answer_id'].iloc[idx]
        answer_id_source = record_df['answer_id_source'].iloc[idx]
        # print(answer_id, answer_id_source)
        query = f"""SELECT * FROM {answer_id_source} WHERE id = {answer_id}"""
        answers_df = pd.read_sql(con=con, sql=query)
        if 'uz' in answers_df.columns:
            answer_uz = answers_df['uz']
        elif 'answer' in answers_df.columns:
            answer_uz = answers_df['answer']
        if 'product' in record_df.iloc[idx]['answer_id_source']:
            column = record_df.iloc[idx]['answer_id_source']
            column = column[column.index('_')+1:]
        else:
            column = record_df.iloc[idx]['answer_type']
        

        temp_out[column] = answer_uz
    temp_out['uuid'] = uuid
    temp_out['date'] = date
    return temp_out

def get_report(responses):
    dates = responses[-1][0].split('-')
    print(responses)
    if dates[0].lower() == 'bugun':
        b_date = datetime.today().date() + timedelta(1)
        a_date = datetime.today().date()
        query = f"""SELECT * FROM survey_response WHERE poll_id = 5 AND date BETWEEN '{a_date}' AND '{b_date}'"""
    elif dates[0].lower() == 'umumiy':
        query = f"""SELECT * FROM survey_response WHERE poll_id = 5"""
    else:
        a_date, b_date = dates[0].strip(), dates[1].strip()
        a_date = datetime.strptime(a_date, "%d.%m.%Y").date()
        b_date = datetime.strptime(b_date, "%d.%m.%Y").date()
        query = f"""SELECT * FROM survey_response WHERE poll_id = 5 AND date BETWEEN '{a_date}' AND '{b_date}'"""
    df = pd.read_sql(con=con, sql=query)
    # print(df)
    print(df)
    if len(df.values) == 0:
        return None
    uuids = df['record_id'].unique().tolist()
    df_out = pd.DataFrame()
    temp_out = pd.DataFrame()
    for uuid in uuids:
        mask = df['record_id'] == uuid
        record_df  = df[mask]
        record_df.reset_index(drop=True, inplace=True)
        date = record_df['date'].values[0]
        
        temp_out  =  generate_report(record_df)        
        df_out = pd.concat([df_out, temp_out], axis=0)

    
    
    df_out.reset_index(inplace=True, drop=True)
    df_out.reset_index(inplace=True)
    df_out['index'] = df_out['index'] + 1
    out_filename = 'report.xlsx'
    df_out =df_out.drop('image', axis=1)
    with pd.ExcelWriter(out_filename , mode='w', engine='openpyxl') as writer:
        df_out.to_excel(writer, index=False)


    return out_filename 

def download_image(url, filename):
    
    filename = os.path.join(media_path, f'{filename}.jpg')
    with open(filename, 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            return False, ''

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

    return True, filename



def transform_to_users_df(df, user_id):
    columns = ['telegram_id', 'telegram_num', 'name', 'surname', 'password_id', 'confirmed', 'date_confirmed', 'date_submitted', 'image']
    user_df = pd.DataFrame(columns=columns)
    user_dict = dict.fromkeys(columns)
    user_dict['telegram_id'] = user_id
    user_dict['confirmed'] = 0
    # user_dict['date_submitted'] = datetime.now()
    answers = []
    for i in df.index:
        answer_id_source = df.iloc[i]['answer_id_source']
        answer_id = df.iloc[i]['answer_id']
        cur = con.cursor()
        print(answer_id, answer_id_source)
        query = f'''SELECT answer FROM {answer_id_source} WHERE id = "{answer_id}"'''
        data = cur.execute(query)
        
        # user_dict[]
        for i, row in enumerate(data):
            answers.append(row[0])
            
    user_dict['name'] = answers[0]
    user_dict['surname'] = answers[1]
    user_dict['telegram_num'] = answers[2]
    user_dict['image'] = answers[3]
    user_authentication = 'employee'
    user_table = 'users_authentication'
    query = f'''SELECT id FROM {user_table} WHERE user_type = "{user_authentication}"'''
    data = cur.execute(query)
    user_dict['password_id'] = [row for row in data][0][0]
    user_df = user_df.append(user_dict, ignore_index=True)
    return user_df

            
# telegram_id = models.IntegerField(null=False, blank=False)
# telegram_num = models.IntegerField(null=False, blank=False)
# name = models.CharField(max_length=512, null=True, blank=True)
# surname = models.CharField(max_length=512, null=True, blank=True)
# password = models.ForeignKey(to=Authentication, on_delete=models.PROTECT)
# confirmed = 
# date = models.


def il_count(s):
    count = 0
    il = ['i', 'l']
    for c in s:
        if c in il:
            count += 1
    return count