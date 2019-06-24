#Import Dependencies
import datetime
import time
from time import gmtime, strftime
import io
import threading
import re
from IPython.display import clear_output
from keras.models import model_from_json
import pickle
import operator
from kafka import KafkaConsumer
import psycopg2
import tensorflow as tf
#Import my functions from the sentiment analysis
import IntentClassification.Intent_Classification_Lai
from IntentClassification.Intent_Classification_Lai import predictions
from IntentClassification.Intent_Classification_Lai import get_final_output


#Establish Connection to PostGres Postgres Information
with open ('PostgresPass.txt', 'r') as file:
    passwordstring = file.readline().split("\n")[0]
try:
    conn = psycopg2.connect(user = "laitcl",
                                 password = passwordstring,
                                 host = "10.0.0.12",
                                 port = "5432",
                                 database = "testpython")
    # create a psycopg2 cursor that can execute queries
    cur = conn.cursor()
    # create a new table with a single column called "name"
    print('Connection to PostgreSQL successful')
except Exception as e:
    print("Can't connect. Invalid dbname, user or password?")
    print(e)

#Define Functions
def processline(line):
    [date, channel, text] = line.split(",",2)
    [date, timeofday] = date.split("_",1)
    text = text.split("\r",1)[0]
    return [date, timeofday, channel, text]

def initializeintentcounter(unique_intent):
    intentdictionary = {}
    for intent in unique_intent:
        intentdictionary[intent] = 0
    return intentdictionary

def getmessagesentiment(channelsentiment, word_tokenizer, text, model, max_length, unique_intent):
    sentiment = get_final_output(predictions(word_tokenizer, text, model, max_length), unique_intent, 'classify')
    channelsentiment[sentiment] += 1#Perform an intent classification
    return channelsentiment

#Load chat classification model
# Model reconstruction from JSON file
with open('IntentClassification/model_architecture.json', 'r') as f1:
    model = model_from_json(f1.read())

# Load weights into the new model
model.load_weights('IntentClassification/model_weights.h5')

#Load Word Tokenizer
with open('IntentClassification/tokenizer.pickle', 'rb') as handle:
    word_tokenizer = pickle.load(handle)

#Load Max Length of a message
with open('IntentClassification/maxlen.txt', 'r') as f2:
    max_length = int(f2.readline())

if __name__ == '__main__':
    #Setup tracking variables
    #For capturing data at set time intervalsmodel
    beginningtime=time.time()
    starttime = time.time()
    logtimeinterval = 5
    #For counting messages
    channelnumlines = {}
    #For intent classification
    channelsentiments = {}
    unique_intent = ['question', 'disappointment', 'funny', 'neutral']

    #Setup Kafka Consumer
    topics = []
    with open ('channellist.txt','r') as source:
        for line in source:
            topics.append(line.split('\n')[0])
    consumer = KafkaConsumer(
        *topics,
         bootstrap_servers=['ec2-3-209-146-134.compute-1.amazonaws.com:9092','ec2-18-205-11-135.compute-1.amazonaws.com:9092','ec2-3-209-201-239.compute-1.amazonaws.com:9092'],
         auto_offset_reset='earliest',
         enable_auto_commit=True,
         group_id='my-group')

        #begin logging chats
    try:
        for message in consumer:
            line = message.value#Takes message from consumer object
            [date,timeofday,channel,text] = processline(line.decode())#Process contents of the message
            if channel not in channelnumlines:
                #If channel wasn't previously tracked, start tracking
                [channelnumlines, channelys, channelxs] = initializenumlines(channel, channelnumlines, channelys, channelxs)
                channelsentiments[channel] = initializeintentcounter(unique_intent)
            channelsentiments[channel] = getmessagesentiment(channelsentiments[channel], word_tokenizer, text, model, max_length, unique_intent)#Increment a sentiment
            channelnumlines[channel] += 1#Increment the number of messages in that channel

            #Every interval, perform analysis
            if time.time() - starttime >= logtimeinterval:
                #clear_output()
                #[channelnumlines, channelsentiments] = animatedplot(channelnumlines, channelxs, channelys, channelsentiments)#Plot the number of messages for each channel
                for channel in channelnumlines:
                    dateandtime = str(time.asctime())
                    latestchannelsentiment = max(channelsentiments[channel].items(), key=operator.itemgetter(1))[0]
                    numlines = channelnumlines[channel]
                    nquestion = channelsentiments[channel]['question']
                    ndisappointment = channelsentiments[channel]['disappointment']
                    nfunny = channelsentiments[channel]['funny']
                    nneutral = channelsentiments[channel]['neutral']
                    sql = """INSERT INTO ChatAnalytics (channelname, date, time, nummessages, question, disappointment, funny, neutral)
                    VALUES(%s, CURRENT_DATE, CURRENT_TIME, %s, %s, %s, %s, %s);"""
                    cur.execute(sql, (channel, numlines, nquestion, ndisappointment, nfunny, nneutral))
                    conn.commit()
                    print("Data point committed at ", datetime.datetime.now())
                    channelnumlines[channel]=0#Reset the number of lines for each channel
                    channelsentiments[channel] = initializeintentcounter(unique_intent)#Reset channel intent
                starttime = time.time()#Reset the start time
    except KeyboardInterrupt:#Let user stop logging when keyboard command is sent
        pass
    conn.close()#Close connection after everything is done
