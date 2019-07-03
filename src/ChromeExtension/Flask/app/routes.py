from flask import render_template, request, redirect
from app import app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.forms import information_form
import os
from pusher import Pusher
import requests, json, atexit, time, plotly, plotly.graph_objs as go
import psycopg2
import operator
import time
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/success')
def success():
    scheduler = BackgroundScheduler()
    # create schedule for retrieving prices
    scheduler.start()
    scheduler.add_job(
        func=retrieve_data,
        trigger=IntervalTrigger(seconds=5),
        id='chat_analytics_retrieval_job',
        name='Retrieve prices every 5 seconds',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    return render_template('index.html', title='Success')

@app.route('/')
@app.route('/', methods=['GET', 'POST'])
def login():
    form = information_form()
    if form.validate_on_submit():
        global channelname
        channelname = form.channelname.data
        return redirect('/success')
    return render_template('form.html', form=form)

# configure pusher object
with open ('pusherinfo.txt', 'r') as file:
    secretstring = file.readline().split("\n")[0]
    pusher = Pusher(
        app_id='811964',
        key='114fb576b66e1ffc4165',
        secret=secretstring,
        cluster='mt1',
        ssl=True
    )

#Establish Connection to PostGres Postgres Information
with open ('PostgresPass.txt', 'r') as file2:
    hostname = file2.readline().split("\n")[0]
    passwordstring = file2.readline().split("\n")[0]
try:
    conn = psycopg2.connect(user = "laitcl",
                                 password = passwordstring,
                                 host = hostname,
                                 port = "5432",
                                 database = "testpython")
    # create a psycopg2 cursor that can execute queries
    cur = conn.cursor()
    # create a new table with a single column called "name"
    print('Connection to PostgreSQL successful')
except Exception as e:
    print("Can't connect. Invalid dbname, user or password?")
    print(e)

# define variables for data retrieval
times = []
nummessages = []

def retrieve_data():
    #Query from PostgreSQL
    timetocollect = 6000
    print("Now tracking ", channelname)
    SQL = "select * from chatanalytics where (extract(epoch from now()::timestamp)-extract(epoch from (date ||' '||time)::timestamp))<%d and channelname = '%s' order by output_id desc limit 10;" % (timetocollect, channelname)
    cur.execute(SQL)
    sqldata = cur.fetchall()

    #Process query
    timevector =[]
    nummessagevector = []
    sentimentvector = []
    sentiment = {}
    for datapoint in sqldata:
        timevector.append(datapoint[3].strftime("%H:%M:%S"))
        nummessagevector.append(datapoint[4])
        nquestion = datapoint[5]
        ndisappointment = datapoint[6]
        nfunny = datapoint[7]
        nneutral = datapoint[8]
        sentiment["question"] = nquestion
        sentiment["disappointment"] = ndisappointment
        sentiment["funny"] = nfunny
        sentiment["neutral"] = nneutral
        latestchannelsentiment = max(sentiment.items(), key=operator.itemgetter(1))[0]
        sentimentvector.append(latestchannelsentiment)

    # create an array of traces for graph data
    graph_data = [go.Scatter(
        x=timevector,
        y=nummessagevector,
        mode='lines+markers+text',
        text=sentimentvector,
        textposition='bottom center',
        name="%s analytics" % (channelname))]

    data = {
        'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
    }

    # trigger event
    pusher.trigger("crypto", "data-updated", data)
