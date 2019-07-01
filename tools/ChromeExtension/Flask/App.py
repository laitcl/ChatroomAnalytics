# ./app.py
from flask import Flask, request, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pusher import Pusher
import requests, json, atexit, time, plotly, plotly.graph_objs as go
import psycopg2
import operator
import time

# create flask app
app = Flask(__name__)

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
with open ('PostgresPass.txt', 'r') as file:
    passwordstring = file.readline().split("\n")[0]
try:
    conn = psycopg2.connect(user = "laitcl",
                                 password = passwordstring,
                                 host = "ec2-3-80-4-183.compute-1.amazonaws.com",
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


@app.route("/")
def index():
    return render_template("index.html")

def retrieve_data():
    #Query from PostgreSQL
    timetocollect = 60
    channelname = 'gamesdonequick'
    SQL = "select * from chatanalytics where (extract(epoch from now()::timestamp)-extract(epoch from (date ||' '||time)::timestamp))<%d and channelname = '%s';" % (timetocollect, channelname)
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

# create schedule for retrieving prices
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=retrieve_data,
    trigger=IntervalTrigger(seconds=5),
    id='chat_analytics_retrieval_job',
    name='Retrieve prices every 5 seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


# run Flask app
app.run(debug=True, use_reloader=False)
