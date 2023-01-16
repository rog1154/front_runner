import pandas as pd
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

def make_race_id_list(year):
    race_id_list = []
    for place in range(1, 11, 1):
        for kai in range(1, 6, 1):
            for day in range(1, 13, 1):
                for r in range(1, 13, 1):
                    race_id = year + str(place).zfill(2) + str(kai).zfill(2) + str(day).zfill(2) + str(r).zfill(2)
                    race_id_list.append(race_id)
    return race_id_list

def make_race_info(race_id_list):
    race_infos ={}
    for race_id in tqdm(race_id_list):
            try:
                filename = "data/race/"+race_id+".bin"
                with open(filename,"rb") as f:
                    html = f.read()
                soup = BeautifulSoup(html,'html.parser')
                texts = soup.find('div',attrs={'class':'data_intro'}).find_all('p')[0].text + soup.find('div',attrs={'class':'data_intro'}).find_all('p')[1].text
                info = re.findall(r'\w+',texts)
                race_infos[race_id] = info
            except:
                continue

    df = pd.DataFrame.from_dict(race_infos,orient='index')
    cols =['種類','距離','馬場','天気','日付']
    race_info_df = pd.DataFrame(columns = cols,index = df.index)
    for index in df.index:
        for i in range(12):
            text = df.at[index,i]
            length = re.compile('(\d+)m').search(text)
            type = re.compile('芝|ダート').search(text)
            turn = re.compile('右|左|障|直線').search(text)
            weather = re.compile('晴|曇|小雨|雨|小雪|雪').search(text)
            condition = re.compile('良|不良|稍重|重').search(text)
            day = re.compile('(\d+年)(\d+)月(\d+)日').search(text)
            if length:
                race_info_df.at[index,'距離'] = length.group()
            if turn:
                if turn.group() == '障':
                    race_info_df.at[index,'種類'] = '障'
                elif turn.group() == '直線':
                    race_info_df.at[index,'種類'] = '直'
            if type:
                if race_info_df.at[index,'種類'] != '障' and race_info_df.at[index,'種類'] != '直':
                    race_info_df.at[index,'種類'] = type.group()
            if condition:
                race_info_df.at[index,'馬場'] = condition.group()
            if weather:
                race_info_df.at[index,'天気'] = weather.group()
            if day:
                race_info_df.at[index,'日付'] = day.group()
    race_info_df['コース'] =''
    for i in race_info_df.index:
        corce_num = i[4:6]
        if corce_num == '01':
            race_info_df.at[i,'コース'] = '札幌'
        elif corce_num == '02':
            race_info_df.at[i,'コース'] = '函館'
        elif corce_num == '03':
            race_info_df.at[i,'コース'] = '福島'
        elif corce_num == '04':
            race_info_df.at[i,'コース'] = '新潟'
        elif corce_num == '05':
            race_info_df.at[i,'コース'] = '東京'
        elif corce_num == '06':
            race_info_df.at[i,'コース'] = '中山'
        elif corce_num == '07':
            race_info_df.at[i,'コース'] = '中京'
        elif corce_num == '08':
            race_info_df.at[i,'コース'] = '京都'
        elif corce_num == '09':
            race_info_df.at[i,'コース'] = '阪神'
        elif corce_num == '10':
            race_info_df.at[i,'コース'] = '小倉'
    race_info_df['日付'] = pd.to_datetime(race_info_df['日付'],format = '%Y年%m月%d日')
    return race_info_df

def make_horse_table(race_id_list,race_info_df):
    cols = ['タイム','上り',
    '距離','種類','馬場','天気','コース',
    '性','年齢','体重','増減','斤量','馬番',
    '前走タイム','前走上り','前走距離','前走種類','前走馬場','前走天気','前走コース','前走体重','前走増減','前走斤量','前走馬番',
    '前々走タイム','前々走上り','前々走距離','前々走種類','前々走馬場','前々走天気','前々走コース','前々走体重','前々走増減','前々走斤量','前々走馬番',
    '3走前タイム','3走前上り','3走前距離','3走前種類','3走前馬場','3走前天気','3走前コース','3走前体重','3走前増減','3走前斤量','3走前馬番',
    '4走前タイム','4走前上り','4走前距離','4走前種類','4走前馬場','4走前天気','4走前コース','4走前体重','4走前増減','4走前斤量','4走前馬番',
    '5走前タイム','5走前上り','5走前距離','5走前種類','5走前馬場','5走前天気','5走前コース','5走前体重','5走前増減','5走前斤量','5走前馬番']
    df = pd.DataFrame(index=[],columns=cols)
    for race_id in tqdm(race_id_list):
        try:
            filename = "data/race/"+race_id+".bin"
            with open(filename,"rb") as f:
                html = f.read()
            soup = BeautifulSoup(html,'html.parser')
            pre_df = pd.read_html(html)[0]
            horse_a_list = soup.find("table", attrs={"summary": "レース結果"}).find_all(
                "a", attrs={"href": re.compile("^/horse")}
            )
            span_list = soup.find_all('span')
            span_list_txt = ''
            for span in span_list:
                span_list_txt += span.get_text()
            up_time_list = re.findall(r"\d\d\.\d", span_list_txt)
            for i in range(18):
                try:
                    horse_num = pre_df.at[i,'馬 番']
                    index_num = race_id + str(horse_num).zfill(2)
                    df.loc[index_num] = 0
                    df.at[index_num,'タイム'] = pre_df.at[i,'タイム']
                    df.at[index_num,'上り'] = up_time_list[i]
                    df.at[index_num,'距離'] = race_info_df.at[race_id,'距離'][:-1]
                    df.at[index_num,'種類'] = race_info_df.at[race_id,'種類']
                    df.at[index_num,'馬場'] = race_info_df.at[race_id,'馬場']
                    df.at[index_num,'天気'] = race_info_df.at[race_id,'天気']
                    df.at[index_num,'コース'] = race_info_df.at[race_id,'コース']
                    df.at[index_num,'性'] = pre_df.at[i,'性齢'][0]
                    df.at[index_num,"年齢"] = pre_df.at[i,"性齢"][1]
                    df.at[index_num,'体重'] = pre_df.at[i,'馬体重'].split("(")[0]
                    df.at[index_num,'増減'] = pre_df.at[i,'馬体重'].split("(")[1][:-1]
                    df.at[index_num,'斤量'] = pre_df.at[i,'斤量']
                    df.at[index_num,'馬番'] = horse_num
                    horse_id = re.findall(r"\d+", horse_a_list[i]["href"])[0]
                    filename = "data/horse/"+horse_id+".bin"
                    with open(filename,"rb") as f:
                        html = f.read()
                    horse_df = pd.read_html(html)[3]
                    horse_df['日付'] = pd.to_datetime(horse_df['日付'])
                    now_race = horse_df[horse_df['日付'] == race_info_df.at[race_id,'日付']]
                    q = now_race.index + 1
                    latest_race = horse_df.iloc[q]
                    df.at[index_num,'前走タイム'] = latest_race['タイム'].values[0]
                    df.at[index_num,'前走上り'] = latest_race['上り'].values[0]
                    df.at[index_num,'前走距離'] = latest_race['距離'].values[0][1:]
                    df.at[index_num,'前走種類'] = latest_race['距離'].values[0][0]
                    df.at[index_num,'前走馬場'] = latest_race['馬 場'].values[0]
                    df.at[index_num,'前走天気'] = latest_race['天 気'].values[0]
                    df.at[index_num,'前走体重'] = latest_race['馬体重'].values[0].split("(")[0]
                    df.at[index_num,'前走増減'] = latest_race['馬体重'].values[0].split("(")[1][:-1]
                    df.at[index_num,'前走斤量'] = latest_race['斤 量'].values[0]
                    df.at[index_num,'前走馬番'] = latest_race['馬 番'].values[0]
                    df.at[index_num,'前走コース'] = re.search(r'\D+',latest_race['開催'].values[0]).group()
                    second_race = horse_df.iloc[q+1]
                    df.at[index_num,'前々走タイム'] = second_race['タイム'].values[0]
                    df.at[index_num,'前々走上り'] = second_race['上り'].values[0]
                    df.at[index_num,'前々走距離'] = second_race['距離'].values[0][1:]
                    df.at[index_num,'前々走種類'] = second_race['距離'].values[0][0]
                    df.at[index_num,'前々走馬場'] = second_race['馬 場'].values[0]
                    df.at[index_num,'前々走天気'] = second_race['天 気'].values[0]
                    df.at[index_num,'前々走体重'] = second_race['馬体重'].values[0].split("(")[0]
                    df.at[index_num,'前々走増減'] = second_race['馬体重'].values[0].split("(")[1][:-1]
                    df.at[index_num,'前々走斤量'] = second_race['斤 量'].values[0]
                    df.at[index_num,'前々走馬番'] = second_race['馬 番'].values[0]
                    df.at[index_num,'前々走コース'] = re.search(r'\D+',second_race['開催'].values[0]).group()
                    third_race = horse_df.iloc[q+2]
                    df.at[index_num,'3走前タイム'] = third_race['タイム'].values[0]
                    df.at[index_num,'3走前上り'] = third_race['上り'].values[0]
                    df.at[index_num,'3走前距離'] = third_race['距離'].values[0][1:]
                    df.at[index_num,'3走前種類'] = third_race['距離'].values[0][0]
                    df.at[index_num,'3走前馬場'] = third_race['馬 場'].values[0]
                    df.at[index_num,'3走前天気'] = third_race['天 気'].values[0]
                    df.at[index_num,'3走前体重'] = third_race['馬体重'].values[0].split("(")[0]
                    df.at[index_num,'3走前増減'] = third_race['馬体重'].values[0].split("(")[1][:-1]
                    df.at[index_num,'3走前斤量'] = third_race['斤 量'].values[0]
                    df.at[index_num,'3走前馬番'] = third_race['馬 番'].values[0]
                    df.at[index_num,'3走前コース'] = re.search(r'\D+',third_race['開催'].values[0]).group()
                    fourth_race = horse_df.iloc[q+3]
                    df.at[index_num,'4走前タイム'] = fourth_race['タイム'].values[0]
                    df.at[index_num,'4走前上り'] = fourth_race['上り'].values[0]
                    df.at[index_num,'4走前距離'] = fourth_race['距離'].values[0][1:]
                    df.at[index_num,'4走前種類'] = fourth_race['距離'].values[0][0]
                    df.at[index_num,'4走前馬場'] = fourth_race['馬 場'].values[0]
                    df.at[index_num,'4走前天気'] = fourth_race['天 気'].values[0]
                    df.at[index_num,'4走前体重'] = fourth_race['馬体重'].values[0].split("(")[0]
                    df.at[index_num,'4走前増減'] = fourth_race['馬体重'].values[0].split("(")[1][:-1]
                    df.at[index_num,'4走前斤量'] = fourth_race['斤 量'].values[0]
                    df.at[index_num,'4走前馬番'] = fourth_race['馬 番'].values[0]
                    df.at[index_num,'4走前コース'] = re.search(r'\D+',fourth_race['開催'].values[0]).group()
                    fifth_race = horse_df.iloc[q+4]
                    df.at[index_num,'5走前タイム'] = fifth_race['タイム'].values[0]
                    df.at[index_num,'5走前上り'] = fifth_race['上り'].values[0]
                    df.at[index_num,'5走前距離'] = fifth_race['距離'].values[0][1:]
                    df.at[index_num,'5走前種類'] = fifth_race['距離'].values[0][0]
                    df.at[index_num,'5走前馬場'] = fifth_race['馬 場'].values[0]
                    df.at[index_num,'5走前天気'] = fifth_race['天 気'].values[0]
                    df.at[index_num,'5走前体重'] = fifth_race['馬体重'].values[0].split("(")[0]
                    df.at[index_num,'5走前増減'] = fifth_race['馬体重'].values[0].split("(")[1][:-1]
                    df.at[index_num,'5走前斤量'] = fifth_race['斤 量'].values[0]
                    df.at[index_num,'5走前馬番'] = fifth_race['馬 番'].values[0]
                    df.at[index_num,'5走前コース'] = re.search(r'\D+',fifth_race['開催'].values[0]).group()
                except:
                    continue
        except:
            continue
    return df

def time_to_sec(horse_table_df,time):
    horse_table_df[time] = horse_table_df[time].astype(str)
    pre_time = horse_table_df[time].str.extract('(\d+):(\d+).(\d+)')
    pre_time.columns=['分','秒','コンマ']
    pre_time =pre_time.fillna(0)
    pre_time['分'] = pre_time['分'].astype(int)
    pre_time['秒'] = pre_time['秒'].astype(int)
    pre_time['コンマ'] = pre_time['コンマ'].astype(int)
    horse_table_df[time] = pre_time['分']*60+pre_time['秒']+pre_time['コンマ']/10
    return horse_table_df
    
def to_int(target):
    try:
        target = int(target)
    except:
        target = 0
    return target

def to_float(target):
    try:
        target = float(target)
    except:
        target = 0.0
    return target

def drop_zero(horse_table_df):
    for id in tqdm(horse_table_df.index):
        if horse_table_df.at[id,'タイム'] == 0:
            horse_table_df.drop(id,inplace = True)
    return horse_table_df

# race_id_list = make_race_id_list('2021')
# race_info_df = make_race_info(race_id_list)
# race_info_df.to_pickle('data/race_info_2021.pickle')

# race_info_df = pd.read_pickle('data/race_info_2021.pickle')

# print(race_info_df[race_info_df.isnull().any(axis=1)])
# race_info_df.at['202104040502','種類'] = 'ダート'
# race_info_df.at['202104040502','馬場'] = '良'
# race_info_df.at['202104040502','天気'] = '曇'
# race_info_df.at['202104040502','日付'] = race_info_df.at['202104040503','日付']
# race_info_df.at['202106010208','日付'] = race_info_df.at['202106010209','日付']
# race_info_df.at['202109021211','日付'] = race_info_df.at['202109021212','日付']
# race_info_df.to_pickle('data/race_info_2021.pickle')

# horse_table_df = make_horse_table(race_info_df.index,race_info_df)
# horse_table_df.to_pickle('data/horse_table_2021.pickle')

# horse_table_df = pd.read_pickle('data/horse_table_2021.pickle')

# horse_table_df = time_to_sec(horse_table_df,'タイム')
# horse_table_df = time_to_sec(horse_table_df,'前走タイム')
# horse_table_df = time_to_sec(horse_table_df,'前々走タイム')
# horse_table_df = time_to_sec(horse_table_df,'3走前タイム')
# horse_table_df = time_to_sec(horse_table_df,'4走前タイム')
# horse_table_df = time_to_sec(horse_table_df,'5走前タイム')
# for id in tqdm(horse_table_df.index):
#     horse_table_df.at[id,'年齢'] = to_int(horse_table_df.at[id,'年齢'])
#     horse_table_df.at[id,'体重'] = to_int(horse_table_df.at[id,'体重'])
#     horse_table_df.at[id,'増減'] = to_int(horse_table_df.at[id,'増減'])
#     horse_table_df.at[id,'距離'] = to_int(horse_table_df.at[id,'距離'])
#     horse_table_df.at[id,'上り'] = to_float(horse_table_df.at[id,'上り'])
#     horse_table_df.at[id,'前走増減'] = to_int(horse_table_df.at[id,'前走増減'])
#     horse_table_df.at[id,'前走体重'] = to_int(horse_table_df.at[id,'前走体重'])
#     horse_table_df.at[id,'前走距離'] = to_int(horse_table_df.at[id,'前走距離'])
#     horse_table_df.at[id,'前走上り'] = to_float(horse_table_df.at[id,'前走上り'])
#     horse_table_df.at[id,'前々走増減'] = to_int(horse_table_df.at[id,'前々走増減'])
#     horse_table_df.at[id,'前々走体重'] = to_int(horse_table_df.at[id,'前々走体重'])
#     horse_table_df.at[id,'前々走距離'] = to_int(horse_table_df.at[id,'前々走距離'])
#     horse_table_df.at[id,'前々走上り'] = to_float(horse_table_df.at[id,'前々走上り'])
#     horse_table_df.at[id,'3走前増減'] = to_int(horse_table_df.at[id,'3走前増減'])
#     horse_table_df.at[id,'3走前体重'] = to_int(horse_table_df.at[id,'3走前体重'])
#     horse_table_df.at[id,'3走前距離'] = to_int(horse_table_df.at[id,'3走前距離'])
#     horse_table_df.at[id,'3走前上り'] = to_float(horse_table_df.at[id,'3走前上り'])
#     horse_table_df.at[id,'4走前増減'] = to_int(horse_table_df.at[id,'4走前増減'])
#     horse_table_df.at[id,'4走前体重'] = to_int(horse_table_df.at[id,'4走前体重'])
#     horse_table_df.at[id,'4走前距離'] = to_int(horse_table_df.at[id,'4走前距離'])
#     horse_table_df.at[id,'4走前上り'] = to_float(horse_table_df.at[id,'4走前上り'])
#     horse_table_df.at[id,'5走前増減'] = to_int(horse_table_df.at[id,'5走前増減'])
#     horse_table_df.at[id,'5走前体重'] = to_int(horse_table_df.at[id,'5走前体重'])
#     horse_table_df.at[id,'5走前距離'] = to_int(horse_table_df.at[id,'5走前距離'])
#     horse_table_df.at[id,'5走前上り'] = to_float(horse_table_df.at[id,'5走前上り'])
# horse_table_df = drop_zero(horse_table_df)
# horse_table_df['上り'] = horse_table_df['上り'].astype('float')
# horse_table_df['体重'] = horse_table_df['体重'].astype('int')
# horse_table_df['増減'] = horse_table_df['増減'].astype('int')
# horse_table_df['距離'] = horse_table_df['距離'].astype('int')
# horse_table_df['前走体重'] = horse_table_df['前走体重'].astype('int')
# horse_table_df['前走増減'] = horse_table_df['前走増減'].astype('int')
# horse_table_df['前走距離'] = horse_table_df['前走距離'].astype('int')
# horse_table_df['前々走体重'] = horse_table_df['前々走体重'].astype('int')
# horse_table_df['前々走増減'] = horse_table_df['前々走増減'].astype('int')
# horse_table_df['前々走距離'] = horse_table_df['前々走距離'].astype('int')
# horse_table_df['3走前体重'] = horse_table_df['3走前体重'].astype('int')
# horse_table_df['3走前増減'] = horse_table_df['3走前増減'].astype('int')
# horse_table_df['3走前距離'] = horse_table_df['3走前距離'].astype('int')
# horse_table_df['4走前体重'] = horse_table_df['4走前体重'].astype('int')
# horse_table_df['4走前増減'] = horse_table_df['4走前増減'].astype('int')
# horse_table_df['4走前距離'] = horse_table_df['4走前距離'].astype('int')
# horse_table_df['5走前体重'] = horse_table_df['5走前体重'].astype('int')
# horse_table_df['5走前増減'] = horse_table_df['5走前増減'].astype('int')
# horse_table_df['5走前距離'] = horse_table_df['5走前距離'].astype('int')
# print(horse_table_df.dtypes)
# horse_table_df.to_pickle('data/horse_table_2021_droped.pickle')
