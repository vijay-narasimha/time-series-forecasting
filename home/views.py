from django.shortcuts import render
# Create your views here.
import pandas as pd
from  matplotlib  import pyplot 
import uuid,base64
from io import BytesIO
from joblib import load
import requests 
from io import BytesIO,StringIO
import h5py
import calendar

# test_url='https://drive.google.com/uc?id=1Bv1B2vUGzi3oL4C6RYO00gnL5M-pHUHr&export=download&confirm=t' 
# response2=requests.get(test_url,allow_redirects=True)
# content2=StringIO(response2.content.decode('utf-8'))
# test_file=pd.read_csv(content2)
 

def get_graph():
    buffer = BytesIO()
    pyplot.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_chart(data, results_by='date',chart_type='line_graph', **kwargs):
    pyplot.switch_backend('AGG')
    fig = pyplot.figure(figsize=(10, 4))
    key=results_by
    
    d = data.groupby(key, as_index=False)['sales'].agg('sum')
    
    if chart_type == 'bar_graph':
        
        pyplot.bar(d[key], d['sales'])
    elif chart_type == 'pie_graph':
        
        pyplot.pie(data=d,x='sales', labels=d[key])
    elif chart_type == 'line_graph':
        
        pyplot.plot( d[key],d['sales'] ,color='blue', marker='o')
    
    else:
        print("Apparently...chart_type not identified")
    pyplot.tight_layout()
    chart = get_graph()
    return chart

def index(req):
    # train_file=pd.read_csv('static/train.csv')
    
    
        
    from_date='2016-01-01'

    to_date='2017-08-15'
    chart_type='line_graph'
    results='date'
    if req.method=='POST':
        # train_url='https://drive.google.com/uc?id=1Bv1B2vUGzi3oL4C6RYO00gnL5M-pHUHr&export=download&confirm=t' 
        # response1=requests.get(train_url,allow_redirects=True)
        # content1=StringIO(response1.content.decode('utf-8'))
        # train_file=pd.read_csv(content1)
        train_file=pd.read_csv('static/train.csv')
        from_date=req.POST.get('from_date')
        
        to_date=req.POST.get("to_date")
        chart_type=req.POST.get('chart_type')
        results=req.POST.get('results')
        
        
        file=train_file[(train_file['date']>=from_date) & (train_file['date']<=to_date)]
        status=1 
        if len(file)==0:
            status=0
        chart=get_chart(file,results,chart_type)
        data={
            'chart':chart,
            'from':from_date,
            'to':to_date,
            'status':status,
            'title':"Analysis",
            'path':'index',
            'location':True,
            
            'display':True,
            'date_from':'2016-01-01',
        'date_to':'2017-08-15'
        }
    else:
        data={'path':'index',
        'location':True,
        'display':False,
        'title':'Analysis',
        'date_from':'2016-01-01',
        'date_to':'2017-08-15'
        }
    
    return render(req,'index.html',data)

def prediction(req):
    

    # model=load('static/model.h5')
    # x=train_file[['dayofweek','store_nbr','family','onpromotion','holidaytype','oil_price','transactions']]
    # y=train_file['sales']
    # model=RandomForestRegressor(n_estimators=1)
    # model.fit(x,y)

    
    
    from_date='2017-08-16'
    to_date='2017-08-31'
    chart_type='line_graph'
    results='date'
    if req.method=='POST':
        
        from_date=req.POST.get('from_date')
        
        to_date=req.POST.get("to_date")
        chart_type=req.POST.get('chart_type')
        results=req.POST.get('results')
        test_file=pd.read_csv("static/test.csv")
        
        # model_url='https://drive.google.com/uc?id=1wwUX80qOiKYPRBlriMHcVAKUo49q4OwJ&export=download&confirm=t'
        # response3=requests.get(model_url,allow_redirects=True)
        # content3=BytesIO(response3.content)
        # model=load(content3)
        model=load('static/model.h5')
        file=test_file[(test_file['date']>=from_date) & (test_file['date']<=to_date)]
        date=pd.DataFrame(file['date'])
        status=1 
        if len(file)==0:
            status=0
        
        # file=file.drop(file.columns[0],axis=1)
        # file=file.drop(columns=['date','test','transferred'])
        
        file1=file[['dayofweek','store_nbr','family','onpromotion','holidaytype','oil_price','transactions']]
        
        sales=pd.DataFrame({'sales':model.predict(file1)})
        
        file=pd.concat([file1,sales,date],axis=1) 

        

        
        chart=get_chart(file,results,chart_type)
        data={
            'chart':chart,
            'from':from_date,
            'to':to_date,
            'status':status,
            'title':"Prediction",
            'path':'predict',
            'location':False,
            'day':False,
            'display':True,
            'date_from':'2017-08-16',
             'date_to':'2017-08-31'
            
        } 
       
    else:
        data={'path':'predict',
        'title':'Prediction',
        'location':False,
        'day':False,
        'display':False,
        'date_from':'2017-08-16',
        'date_to':'2017-08-31'

        }
    
    return render(req,'index.html',data)
    

def dayanalysis(req):
    if req.method=='POST':
        model=load('static/model.h5')

        from_date=req.POST.get('from_date')
        store_id=req.POST.get('store_id')
        family=req.POST.get('family')
        promotion=req.POST.get('promotion')
        oil_price=req.POST.get('oil_price')
        transactions=req.POST.get("transactions")
        year,month,day=(int(i) for i in from_date.split('-'))
        dayofweek=calendar.weekday(year,month,day)+1
        familydict={
                'AUTOMOTIVE':0,
                "BEAUTY":2,
                'BOOKS':4,
                'HARDWARE':14,
                'MAGAZINES':23,
                'PET SUPPLIES':26,
                'ELECTRONICS':27
            }

        if dayofweek>5:
            holiday=1 
        else:
            holiday=5 
        store_nbr=store_id
        promotion=promotion
        oil_price=oil_price
        family=familydict[family]
        transactions=transactions
        print([[dayofweek,store_nbr,family,promotion,holiday,oil_price,transactions]])
        
        result=model.predict([[dayofweek,store_nbr,family,promotion,holiday,oil_price,transactions]])
        result=round(result[0],2)
        data={
            'location':False,
            'day':True,
            'path':'day',
            'result':result,
            'title':'Day Analysis'
        }
    else:

        data={
            'location':False,
            'day':True,
            'path':'day',
            'title':'Day Analysis'
        }
    return render(req,'day.html',data)