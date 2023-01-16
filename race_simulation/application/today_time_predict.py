import pandas as pd
import pickle
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import time
import requests
import lightgbm as lgb
import numpy as np
from race_simulation.application import make_data

def scrape(race_id,date):
    url = "https://race.netkeiba.com/race/shutuba.html?race_id=" + race_id
    time.sleep(0.5)
    html = requests.get(url)
    html.encoding = 'EUC-JP'
    soup = BeautifulSoup(html.text,'html.parser')
    try:
        texts = soup.find('div',attrs={'class':'RaceData01'}).text
    except:
        return pd.DataFrame()
    info = re.findall(r'\w+',texts)
    cols =['種類','距離','馬場','天気','日付']
    race_info_df = pd.DataFrame(columns = cols,index = [race_id])
    for i in range(len(info)):
        text = info[i]
        length = re.compile('(\d+)m').search(text)
        type = re.compile('芝|ダ').search(text)
        turn = re.compile('右|左|障|直線').search(text)
        weather = re.compile('晴|曇|小雨|雨|小雪|雪').search(text)
        condition = re.compile('良|不良|稍|重').search(text)
        if length:
            race_info_df.at[race_id,'距離'] = length.group()
        if turn:
            if turn.group() == '障':
                race_info_df.at[race_id,'種類'] = '障'
            elif turn.group() == '直線':
                race_info_df.at[race_id,'種類'] = '直'
        if type:
            if race_info_df.at[race_id,'種類'] != '障' and race_info_df.at[race_id,'種類'] != '直':
                if type.group() == 'ダ':
                    race_info_df.at[race_id,'種類'] = 'ダート'
                else:
                    race_info_df.at[race_id,'種類'] = type.group()
        if condition:
            if condition.group() == '稍':
                race_info_df.at[race_id,'馬場'] = '稍重'
            else:
                race_info_df.at[race_id,'馬場'] = condition.group()
        if weather:
            race_info_df.at[race_id,'天気'] = weather.group()
    race_info_df['コース'] =''
    corce_num = race_id[4:6]
    if corce_num == '01':
        race_info_df.at[race_id,'コース'] = '札幌'
    elif corce_num == '02':
        race_info_df.at[race_id,'コース'] = '函館'
    elif corce_num == '03':
        race_info_df.at[race_id,'コース'] = '福島'
    elif corce_num == '04':
        race_info_df.at[race_id,'コース'] = '新潟'
    elif corce_num == '05':
        race_info_df.at[race_id,'コース'] = '東京'
    elif corce_num == '06':
        race_info_df.at[race_id,'コース'] = '中山'
    elif corce_num == '07':
        race_info_df.at[race_id,'コース'] = '中京'
    elif corce_num == '08':
        race_info_df.at[race_id,'コース'] = '京都'
    elif corce_num == '09':
        race_info_df.at[race_id,'コース'] = '阪神'
    elif corce_num == '10':
        race_info_df.at[race_id,'コース'] = '小倉'
    race_info_df.at[race_id,'日付'] = pd.to_datetime(date)
    cols = ['タイム','上り',
    '距離','種類','馬場','天気','コース',
    '性','年齢','体重','増減','斤量','馬番',
    '前走タイム','前走上り','前走距離','前走種類','前走馬場','前走天気','前走コース','前走体重','前走増減','前走斤量','前走馬番',
    '前々走タイム','前々走上り','前々走距離','前々走種類','前々走馬場','前々走天気','前々走コース','前々走体重','前々走増減','前々走斤量','前々走馬番',
    '3走前タイム','3走前上り','3走前距離','3走前種類','3走前馬場','3走前天気','3走前コース','3走前体重','3走前増減','3走前斤量','3走前馬番',
    '4走前タイム','4走前上り','4走前距離','4走前種類','4走前馬場','4走前天気','4走前コース','4走前体重','4走前増減','4走前斤量','4走前馬番',
    '5走前タイム','5走前上り','5走前距離','5走前種類','5走前馬場','5走前天気','5走前コース','5走前体重','5走前増減','5走前斤量','5走前馬番']
    horse_table_df = pd.DataFrame(index=[],columns=cols)
    pre_df = pd.read_html(url)[0]
    horse_a_list = soup.find("table", attrs={"class": "Shutuba_Table"}).find_all('a',attrs={'href':re.compile('^https://db.netkeiba.com/horse/')})
    for i in tqdm(range(18)):
        try:
            horse_num = pre_df.loc[i,'馬 番'][0]
            index_num = race_id + str(horse_num).zfill(2)
            horse_table_df.loc[index_num] = 0
            horse_table_df.at[index_num,'距離'] = race_info_df.at[race_id,'距離'][:-1]
            horse_table_df.at[index_num,'種類'] = race_info_df.at[race_id,'種類']
            horse_table_df.at[index_num,'馬場'] = race_info_df.at[race_id,'馬場']
            horse_table_df.at[index_num,'天気'] = race_info_df.at[race_id,'天気']
            horse_table_df.at[index_num,'コース'] = race_info_df.at[race_id,'コース']
            horse_table_df.at[index_num,'性'] = pre_df.loc[i,'性齢'][0][0]
            horse_table_df.at[index_num,"年齢"] = pre_df.loc[i,"性齢"][0][1]
            try:
                horse_table_df.at[index_num,'体重'] = pre_df.loc[i,'馬体重 (増減)'][0].split("(")[0]
                horse_table_df.at[index_num,'増減'] = pre_df.loc[i,'馬体重 (増減)'][0].split("(")[1][:-1]
            except:
                horse_table_df.at[index_num,'体重'] = 0
                horse_table_df.at[index_num,'増減'] = 0
            horse_table_df.at[index_num,'斤量'] = pre_df.loc[i,'斤量'][0]
            horse_table_df.at[index_num,'馬番'] = horse_num
            horse_id = re.findall(r"\d+", horse_a_list[i]["href"])[0]
            url = "https://db.netkeiba.com/horse/" + horse_id
            time.sleep(0.5)
            html = requests.get(url)
            html.encoding = 'EUC-JP'
            soup = BeautifulSoup(html.text,'html.parser')
            horse_df = pd.read_html(url)[3]
            horse_df['日付'] = pd.to_datetime(horse_df['日付'])
            q = 0
            if horse_df.iat[0,0] == race_info_df.at[race_id,'日付']:
                q = 1
            latest_race = horse_df.iloc[q]
            horse_table_df.at[index_num,'前走タイム'] = latest_race['タイム']
            horse_table_df.at[index_num,'前走上り'] = latest_race['上り']
            horse_table_df.at[index_num,'前走距離'] = latest_race['距離'][1:]
            horse_table_df.at[index_num,'前走種類'] = latest_race['距離'][0]
            horse_table_df.at[index_num,'前走馬場'] = latest_race['馬 場']
            horse_table_df.at[index_num,'前走天気'] = latest_race['天 気']
            horse_table_df.at[index_num,'前走体重'] = latest_race['馬体重'].split("(")[0]
            horse_table_df.at[index_num,'前走増減'] = latest_race['馬体重'].split("(")[1][:-1]
            horse_table_df.at[index_num,'前走斤量'] = latest_race['斤 量']
            horse_table_df.at[index_num,'前走馬番'] = latest_race['馬 番']
            horse_table_df.at[index_num,'前走コース'] = re.search(r'\D+',latest_race['開催']).group()
            second_race = horse_df.iloc[q+1]
            horse_table_df.at[index_num,'前々走タイム'] = second_race['タイム']
            horse_table_df.at[index_num,'前々走上り'] = second_race['上り']
            horse_table_df.at[index_num,'前々走距離'] = second_race['距離'][1:]
            horse_table_df.at[index_num,'前々走種類'] = second_race['距離'][0]
            horse_table_df.at[index_num,'前々走馬場'] = second_race['馬 場']
            horse_table_df.at[index_num,'前々走天気'] = second_race['天 気']
            horse_table_df.at[index_num,'前々走体重'] = second_race['馬体重'].split("(")[0]
            horse_table_df.at[index_num,'前々走増減'] = second_race['馬体重'].split("(")[1][:-1]
            horse_table_df.at[index_num,'前々走斤量'] = second_race['斤 量']
            horse_table_df.at[index_num,'前々走馬番'] = second_race['馬 番']
            horse_table_df.at[index_num,'前々走コース'] = re.search(r'\D+',second_race['開催']).group()
            third_race = horse_df.iloc[q+2]
            horse_table_df.at[index_num,'3走前タイム'] = third_race['タイム']
            horse_table_df.at[index_num,'3走前上り'] = third_race['上り']
            horse_table_df.at[index_num,'3走前距離'] = third_race['距離'][1:]
            horse_table_df.at[index_num,'3走前種類'] = third_race['距離'][0]
            horse_table_df.at[index_num,'3走前馬場'] = third_race['馬 場']
            horse_table_df.at[index_num,'3走前天気'] = third_race['天 気']
            horse_table_df.at[index_num,'3走前体重'] = third_race['馬体重'].split("(")[0]
            horse_table_df.at[index_num,'3走前増減'] = third_race['馬体重'].split("(")[1][:-1]
            horse_table_df.at[index_num,'3走前斤量'] = third_race['斤 量']
            horse_table_df.at[index_num,'3走前馬番'] = third_race['馬 番']
            horse_table_df.at[index_num,'3走前コース'] = re.search(r'\D+',third_race['開催']).group()
            fourth_race = horse_df.iloc[q+3]
            horse_table_df.at[index_num,'4走前タイム'] = fourth_race['タイム']
            horse_table_df.at[index_num,'4走前上り'] = fourth_race['上り']
            horse_table_df.at[index_num,'4走前距離'] = fourth_race['距離'][1:]
            horse_table_df.at[index_num,'4走前種類'] = fourth_race['距離'][0]
            horse_table_df.at[index_num,'4走前馬場'] = fourth_race['馬 場']
            horse_table_df.at[index_num,'4走前天気'] = fourth_race['天 気']
            horse_table_df.at[index_num,'4走前体重'] = fourth_race['馬体重'].split("(")[0]
            horse_table_df.at[index_num,'4走前増減'] = fourth_race['馬体重'].split("(")[1][:-1]
            horse_table_df.at[index_num,'4走前斤量'] = fourth_race['斤 量']
            horse_table_df.at[index_num,'4走前馬番'] = fourth_race['馬 番']
            horse_table_df.at[index_num,'4走前コース'] = re.search(r'\D+',fourth_race['開催']).group()
            fifth_race = horse_df.iloc[q+4]
            horse_table_df.at[index_num,'5走前タイム'] = fifth_race['タイム']
            horse_table_df.at[index_num,'5走前上り'] = fifth_race['上り']
            horse_table_df.at[index_num,'5走前距離'] = fifth_race['距離'][1:]
            horse_table_df.at[index_num,'5走前種類'] = fifth_race['距離'][0]
            horse_table_df.at[index_num,'5走前馬場'] = fifth_race['馬 場']
            horse_table_df.at[index_num,'5走前天気'] = fifth_race['天 気']
            horse_table_df.at[index_num,'5走前体重'] = fifth_race['馬体重'].split("(")[0]
            horse_table_df.at[index_num,'5走前増減'] = fifth_race['馬体重'].split("(")[1][:-1]
            horse_table_df.at[index_num,'5走前斤量'] = fifth_race['斤 量']
            horse_table_df.at[index_num,'5走前馬番'] = fifth_race['馬 番']
            horse_table_df.at[index_num,'5走前コース'] = re.search(r'\D+',fifth_race['開催']).group()
        except:
            continue
    horse_table_df = horse_table_df.to_json()
    return horse_table_df
    

def predict(race_id,horse_table_df):
    horse_table_df = pd.read_json(horse_table_df)
    model1 = pickle.load(open('data/model/total_time_pred.pkl','rb'))
    model2 = pickle.load(open('data/model/up_time_pred.pkl','rb'))
    horse_table_df = make_data.time_to_sec(horse_table_df,'タイム')
    horse_table_df = make_data.time_to_sec(horse_table_df,'前走タイム')
    horse_table_df = make_data.time_to_sec(horse_table_df,'前々走タイム')
    horse_table_df = make_data.time_to_sec(horse_table_df,'3走前タイム')
    horse_table_df = make_data.time_to_sec(horse_table_df,'4走前タイム')
    horse_table_df = make_data.time_to_sec(horse_table_df,'5走前タイム')
    for id in tqdm(horse_table_df.index):
        horse_table_df.at[id,'年齢'] = make_data.to_int(horse_table_df.at[id,'年齢'])
        horse_table_df.at[id,'体重'] = make_data.to_int(horse_table_df.at[id,'体重'])
        horse_table_df.at[id,'増減'] = make_data.to_int(horse_table_df.at[id,'増減'])
        horse_table_df.at[id,'距離'] = make_data.to_int(horse_table_df.at[id,'距離'])
        horse_table_df.at[id,'上り'] = make_data.to_float(horse_table_df.at[id,'上り'])
        horse_table_df.at[id,'前走増減'] = make_data.to_int(horse_table_df.at[id,'前走増減'])
        horse_table_df.at[id,'前走体重'] = make_data.to_int(horse_table_df.at[id,'前走体重'])
        horse_table_df.at[id,'前走距離'] = make_data.to_int(horse_table_df.at[id,'前走距離'])
        horse_table_df.at[id,'前走上り'] = make_data.to_float(horse_table_df.at[id,'前走上り'])
        horse_table_df.at[id,'前々走増減'] = make_data.to_int(horse_table_df.at[id,'前々走増減'])
        horse_table_df.at[id,'前々走体重'] = make_data.to_int(horse_table_df.at[id,'前々走体重'])
        horse_table_df.at[id,'前々走距離'] = make_data.to_int(horse_table_df.at[id,'前々走距離'])
        horse_table_df.at[id,'前々走上り'] = make_data.to_float(horse_table_df.at[id,'前々走上り'])
        horse_table_df.at[id,'3走前増減'] = make_data.to_int(horse_table_df.at[id,'3走前増減'])
        horse_table_df.at[id,'3走前体重'] = make_data.to_int(horse_table_df.at[id,'3走前体重'])
        horse_table_df.at[id,'3走前距離'] = make_data.to_int(horse_table_df.at[id,'3走前距離'])
        horse_table_df.at[id,'3走前上り'] = make_data.to_float(horse_table_df.at[id,'3走前上り'])
        horse_table_df.at[id,'4走前増減'] = make_data.to_int(horse_table_df.at[id,'4走前増減'])
        horse_table_df.at[id,'4走前体重'] = make_data.to_int(horse_table_df.at[id,'4走前体重'])
        horse_table_df.at[id,'4走前距離'] = make_data.to_int(horse_table_df.at[id,'4走前距離'])
        horse_table_df.at[id,'4走前上り'] = make_data.to_float(horse_table_df.at[id,'4走前上り'])
        horse_table_df.at[id,'5走前増減'] = make_data.to_int(horse_table_df.at[id,'5走前増減'])
        horse_table_df.at[id,'5走前体重'] = make_data.to_int(horse_table_df.at[id,'5走前体重'])
        horse_table_df.at[id,'5走前距離'] = make_data.to_int(horse_table_df.at[id,'5走前距離'])
        horse_table_df.at[id,'5走前上り'] = make_data.to_float(horse_table_df.at[id,'5走前上り'])
    horse_table_df['上り'] = horse_table_df['上り'].astype('float')
    horse_table_df['体重'] = horse_table_df['体重'].astype('int')
    horse_table_df['増減'] = horse_table_df['増減'].astype('int')
    horse_table_df['距離'] = horse_table_df['距離'].astype('int')
    horse_table_df['前走体重'] = horse_table_df['前走体重'].astype('int')
    horse_table_df['前走増減'] = horse_table_df['前走増減'].astype('int')
    horse_table_df['前走距離'] = horse_table_df['前走距離'].astype('int')
    horse_table_df['前々走体重'] = horse_table_df['前々走体重'].astype('int')
    horse_table_df['前々走増減'] = horse_table_df['前々走増減'].astype('int')
    horse_table_df['前々走距離'] = horse_table_df['前々走距離'].astype('int')
    horse_table_df['3走前体重'] = horse_table_df['3走前体重'].astype('int')
    horse_table_df['3走前増減'] = horse_table_df['3走前増減'].astype('int')
    horse_table_df['3走前距離'] = horse_table_df['3走前距離'].astype('int')
    horse_table_df['4走前体重'] = horse_table_df['4走前体重'].astype('int')
    horse_table_df['4走前増減'] = horse_table_df['4走前増減'].astype('int')
    horse_table_df['4走前距離'] = horse_table_df['4走前距離'].astype('int')
    horse_table_df['5走前体重'] = horse_table_df['5走前体重'].astype('int')
    horse_table_df['5走前増減'] = horse_table_df['5走前増減'].astype('int')
    horse_table_df['5走前距離'] = horse_table_df['5走前距離'].astype('int')
    horse_len = len(horse_table_df.index)
    horse_table_df1 = pd.read_pickle('data/horse_table_2018_droped.pickle')
    horse_table_df2 = pd.read_pickle('data/horse_table_2019_droped.pickle')
    horse_table_df3 = pd.read_pickle('data/horse_table_2020_droped.pickle')
    horse_table_df4 = pd.read_pickle('data/horse_table_2021_droped.pickle')
    horse_table_df = pd.concat([horse_table_df1,horse_table_df2,horse_table_df3,horse_table_df4,horse_table_df])
    horse_table_df.drop(columns='タイム',inplace=True)
    horse_table_df.drop(columns='上り',inplace=True)
    horse_table_df = pd.get_dummies(horse_table_df)
    horse_table_df.to_csv('data/horse_table_df.csv')
    horse_table_df = horse_table_df.iloc[-horse_len:]
    total_time_pred = model1.predict(horse_table_df)
    up_time_pred = model2.predict(horse_table_df)
    pred_df = pd.DataFrame({"予想タイム": total_time_pred,"予想上りタイム": up_time_pred})
    pred_df.index = horse_table_df.index
    cols = ['予想タイム01','予想タイム02','予想タイム03','予想タイム04','予想タイム05','予想タイム06','予想タイム07','予想タイム08','予想タイム09',
            '予想タイム10','予想タイム11','予想タイム12','予想タイム13','予想タイム14','予想タイム15','予想タイム16','予想タイム17','予想タイム18',
            '予想上りタイム01','予想上りタイム02','予想上りタイム03','予想上りタイム04','予想上りタイム05','予想上りタイム06','予想上りタイム07','予想上りタイム08','予想上りタイム09',
            '予想上りタイム10','予想上りタイム11','予想上りタイム12','予想上りタイム13','予想上りタイム14','予想上りタイム15','予想上りタイム16','予想上りタイム17','予想上りタイム18']
    time_pred = pd.DataFrame(index = [race_id],columns = cols)
    for id in pred_df.index:
        horse_num = str(id)[-2:]
        time_pred.at[race_id,'予想タイム'+str(horse_num)] = pred_df.at[id,'予想タイム']
        time_pred.at[race_id,'予想上りタイム'+str(horse_num)] = pred_df.at[id,'予想上りタイム']
    time_pred = time_pred.fillna(0)
    return time_pred
        