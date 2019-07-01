# Import Dependencies
import datetime
import io
import threading
import re
import operator
import os
import time
from time import gmtime, strftime
from keras.models import model_from_json
import pickle
from kafka import KafkaConsumer
import psycopg2
import tensorflow as tf
# Import my functions from the sentiment analysis
import Intent_Classification_Lai
from Intent_Classification_Lai import predictions
from Intent_Classification_Lai import get_final_output


# Establish Connection to PostGres Postgres Information
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__,'PostgresPass.txt'), 'r') as file:
    passwordstring = file.readline().split("\n")[0]
try:
    conn = psycopg2.connect(user="laitcl",
                                 password=passwordstring,
                                 host="10.0.0.12",
                                 port="5432",
                                 database="testpython")
    # create a psycopg2 cursor that can execute queries
    cur = conn.cursor()
    # create a new table with a single column called "name"
    print('Connection to PostgreSQL successful')
except Exception as e:
    print("Can't connect. Invalid dbname, user or password?")
    print(e)

# Define Functions
#Method to process one line of messages
def processline(line):
    [date, channel, text] = line.split(",", 2)
    [date, timeofday] = date.split("_", 1)
    text = text.split("\r", 1)[0]
    return [date, timeofday, channel, text]

# Load chat classification model
# Model reconstruction from JSON file
with open(os.path.join(__location__,'../../tools/IntentClassification/model_architecture.json'), 'r') as f1:
    model = model_from_json(f1.read())

# Load weights into the new model
model.load_weights(os.path.join(__location__,'../../tools/IntentClassification/model_weights.h5'))

# Load Word Tokenizer
with open(os.path.join(__location__,'../../tools/IntentClassification/tokenizer.pickle'), 'rb') as handle:
    word_tokenizer = pickle.load(handle)

# Load Max Length of a message
with open(os.path.join(__location__,'../../tools/IntentClassification/maxlen.txt'), 'r') as f2:
    max_length = int(f2.readline())

# Setup Kafka Consumer

topics = ['twitchmessages'])
consumer = KafkaConsumer(
    *topics,
     bootstrap_servers=['ec2-3-209-146-134.compute-1.amazonaws.com:9092', 'ec2-18-205-11-135.compute-1.amazonaws.com:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group')

#Setup channel analytics class for consumer code
class channelanalytics:
    def __init__(self):
        #Logging Channel Analytics
        self.channelnumlines = {}
        self.channelsentiments = {}
        self.unique_intent = ['question', 'disappointment', 'funny', 'neutral']
        #Logging Time
        self.beginningtime = time.time()
        self.starttime = time.time()
        self.logtimeinterval = 5

    def initializecounter(self, channel):
        self.channelnumlines[channel] = 0
        self.channelsentiments[channel] = {}
        for intent in self.unique_intent:
            self.channelsentiments[channel][intent] = 0

    def incrementchannel(self, channel, message):
        self.channelnumlines[channel] += 1
        sentiment = get_final_output(
        predictions(
            word_tokenizer,
            text,
            model,
            max_length),
            self.unique_intent,
             'classify')#Perform an intent classification
        self.channelsentiments[channel][sentiment] += 1

    def databaseupdate(self,channel):
        dateandtime = str(time.asctime())
        numlines = self.channelnumlines[channel]
        lastsentiment = {}
        for intent in self.unique_intent:
            lastsentiment[intent] = self.channelsentiments[channel][intent]
        sql = """INSERT INTO ChatAnalytics (channelname, date, time, nummessages, question, disappointment, funny, neutral)
        VALUES(%s, CURRENT_DATE, CURRENT_TIME, %s, %s, %s, %s, %s);"""
        cur.execute(
        sql,
        (channel,
        numlines,
        lastsentiment['question'],
        lastsentiment['disappointment'],
        lastsentiment['funny'],
        lastsentiment['neutral']))
        conn.commit()
        print("Data point committed at ", datetime.datetime.now())

if __name__ == '__main__':
    # Setup tracking variables
    channels = channelanalytics()
    # begin logging chats
    try:
        for message in consumer:
            line = message.value  # Takes message from consumer object
            [date, timeofday, channel, text]= processline(line.decode())  # Process contents of the message
            if channel not in channels.channelnumlines:  # If channel wasn't previously tracked, start tracking
                channels.initializecounter(channel)
            channels.incrementchannel(channel, text)# Increment a sentiment and number of lines
            if time.time() - channels.starttime >= channels.logtimeinterval:# Every interval, perform analysis
                for channel in channels.channelnumlines:
                    channels.databaseupdate(channel)#Export information to database
                    channels.initializecounter(channel)#Reinitalize counter for next cycle
                channels.starttime = time.time()  # Reset the start time
    except KeyboardInterrupt:  # Let user stop logging when keyboard command is sent
        conn.close()  # Close connection after everything is done
