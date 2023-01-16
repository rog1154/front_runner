from django.shortcuts import render
from .models import RaceData
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re
from .application import today_time_predict
from django.shortcuts import redirect

# Create your views here.
def index(request):
    # data1 = pd.read_pickle('data/time_pred_2018-2021.pickle')
    # data2 = pd.read_pickle('data/up_time_pred_2018-2021.pickle')
    # for id in tqdm(data1.index):
    #     RaceData.objects.update_or_create(race_id = id,
    #     total_time1 = data1.at[id,'予想タイム01'],
    #     total_time2 = data1.at[id,'予想タイム02'],
    #     total_time3 = data1.at[id,'予想タイム03'],
    #     total_time4 = data1.at[id,'予想タイム04'],
    #     total_time5 = data1.at[id,'予想タイム05'],
    #     total_time6 = data1.at[id,'予想タイム06'],
    #     total_time7 = data1.at[id,'予想タイム07'],
    #     total_time8 = data1.at[id,'予想タイム08'],
    #     total_time9 = data1.at[id,'予想タイム09'],
    #     total_time10 = data1.at[id,'予想タイム10'],
    #     total_time11 = data1.at[id,'予想タイム11'],
    #     total_time12 = data1.at[id,'予想タイム12'],
    #     total_time13 = data1.at[id,'予想タイム13'],
    #     total_time14 = data1.at[id,'予想タイム14'],
    #     total_time15 = data1.at[id,'予想タイム15'],
    #     total_time16 = data1.at[id,'予想タイム16'],
    #     total_time17 = data1.at[id,'予想タイム17'],
    #     total_time18 = data1.at[id,'予想タイム18'],
    #     up_time1 = data2.at[id,'予想タイム01'],
    #     up_time2 = data2.at[id,'予想タイム02'],
    #     up_time3 = data2.at[id,'予想タイム03'],
    #     up_time4 = data2.at[id,'予想タイム04'],
    #     up_time5 = data2.at[id,'予想タイム05'],
    #     up_time6 = data2.at[id,'予想タイム06'],
    #     up_time7 = data2.at[id,'予想タイム07'],
    #     up_time8 = data2.at[id,'予想タイム08'],
    #     up_time9 = data2.at[id,'予想タイム09'],
    #     up_time10 = data2.at[id,'予想タイム10'],
    #     up_time11 = data2.at[id,'予想タイム11'],
    #     up_time12 = data2.at[id,'予想タイム12'],
    #     up_time13 = data2.at[id,'予想タイム13'],
    #     up_time14 = data2.at[id,'予想タイム14'],
    #     up_time15 = data2.at[id,'予想タイム15'],
    #     up_time16 = data2.at[id,'予想タイム16'],
    #     up_time17 = data2.at[id,'予想タイム17'],
    #     up_time18 = data2.at[id,'予想タイム18']
    #     )
    return render(request,'race_simulation/index.html')

def simulate(request,id):
    try:
        data = RaceData.objects.get(race_id = id)
    except:
        horse_table_df = request.session['data']
        time_pred = today_time_predict.predict(id,horse_table_df)
        if time_pred.empty:
            data = {}
        else:
            data = {'race_id' : id,
                'total_time1' : time_pred.at[id,'予想タイム01'],
                'total_time2' : time_pred.at[id,'予想タイム02'],
                'total_time3' : time_pred.at[id,'予想タイム03'],
                'total_time4' : time_pred.at[id,'予想タイム04'],
                'total_time5' : time_pred.at[id,'予想タイム05'],
                'total_time6' : time_pred.at[id,'予想タイム06'],
                'total_time7' : time_pred.at[id,'予想タイム07'],
                'total_time8' : time_pred.at[id,'予想タイム08'],
                'total_time9' : time_pred.at[id,'予想タイム09'],
                'total_time10' : time_pred.at[id,'予想タイム10'],
                'total_time11' : time_pred.at[id,'予想タイム11'],
                'total_time12' : time_pred.at[id,'予想タイム12'],
                'total_time13' : time_pred.at[id,'予想タイム13'],
                'total_time14' : time_pred.at[id,'予想タイム14'],
                'total_time15' : time_pred.at[id,'予想タイム15'],
                'total_time16' : time_pred.at[id,'予想タイム16'],
                'total_time17' : time_pred.at[id,'予想タイム17'],
                'total_time18' : time_pred.at[id,'予想タイム18'],
                'up_time1' : time_pred.at[id,'予想上りタイム01'],
                'up_time2' : time_pred.at[id,'予想上りタイム02'],
                'up_time3' : time_pred.at[id,'予想上りタイム03'],
                'up_time4' : time_pred.at[id,'予想上りタイム04'],
                'up_time5' : time_pred.at[id,'予想上りタイム05'],
                'up_time6' : time_pred.at[id,'予想上りタイム06'],
                'up_time7' : time_pred.at[id,'予想上りタイム07'],
                'up_time8' : time_pred.at[id,'予想上りタイム08'],
                'up_time9' : time_pred.at[id,'予想上りタイム09'],
                'up_time10' : time_pred.at[id,'予想上りタイム10'],
                'up_time11' : time_pred.at[id,'予想上りタイム11'],
                'up_time12' : time_pred.at[id,'予想上りタイム12'],
                'up_time13' : time_pred.at[id,'予想上りタイム13'],
                'up_time14' : time_pred.at[id,'予想上りタイム14'],
                'up_time15' : time_pred.at[id,'予想上りタイム15'],
                'up_time16' : time_pred.at[id,'予想上りタイム16'],
                'up_time17' : time_pred.at[id,'予想上りタイム17'],
                'up_time18' : time_pred.at[id,'予想上りタイム18']
                }
    context = {'data':data}
    return render(request,'race_simulation/simulate.html',context)

def race_list(request):
    date = request.GET['date']
    date = date.replace('-','')
    url = "https://orepro.netkeiba.com/bet/race_list.html?&kaisai_date="+ date
    html = requests.get(url)
    html.encoding = 'EUC-JP'
    soup = BeautifulSoup(html.text,'html.parser')
    texts = soup.findAll('a',attrs={'href':re.compile('^race_list.html\?kaisai_id=')})
    id_list=[]
    for a in texts:
        id = re.findall(r'\d{10}',a["href"])
        for i in range(1,13):
            id_list.append([id[0]+str(i).zfill(2),a.string+str(i)+'R'])
        # url = "https://orepro.netkeiba.com/bet/race_list.html?kaisai_id="+ id[0] +"&kaisai_date="+ date
        # html = requests.get(url)
        # html.encoding = 'EUC-JP'
        # soup = BeautifulSoup(html.text,'html.parser')
        # texts = soup.findAll('dt',attrs={'class':'Race_Name'})
    hiduke = date[:4]+'年'+date[4:6]+'月'+date[6:]+'日'
    context = {'id_list':id_list,'date':date,'hiduke':hiduke}
    return render(request,'race_simulation/race_list.html',context)

def scrape_race(request,date,id):
    if RaceData.objects.filter(race_id = id).exists():
        pass
    else:
        request.session['data'] = today_time_predict.scrape(id,date)
    return redirect('race_simulation:simulate',id)
