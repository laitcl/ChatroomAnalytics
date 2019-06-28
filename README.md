# Conversation Headline Analytics Tool (CHAT)

<div style="text-align:center; margin: 50px 0"><img src ="ChromeExtension/extension/images/icon.png" height="150"/></div>

The tool CHAT ingests Twitch TV messages and outputs message count and channel one of four audience sentiments (Question, Disappointment, Funny, and Neutral) every five seconds for each channel. This information is outputted through a chrome extension for content creators to observe superficial audience behavior.

## Getting Started

To gain a copy of this project and test this project:
`git clone https://github.com/laitcl/ChatroomAnalytics.git`

Fill in the credential documents with your own accounts. They are located in the following in the following
```
PostgresPass.txt
TwitchBot/credential.js
ChromeExtension/Flask/PostgresPass.txt
ChromeExtension/Flask/pusherinfo.txt
```

Point towards the correct servers of Kafka-Brokers

In consumer.py
```
consumer = KafkaConsumer(
    *topics,
     bootstrap_servers=['ec2-3-209-146-134.compute-1.amazonaws.com:9092', 'ec2-18-205-11-135.compute-1.amazonaws.com:9092', 'ec2 - 3 - 209 - 201 -$
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group')
```

In TwitchBot/chatbot_Lai.js
```
  var stream = Kafka.Producer.createWriteStream({
    'metadata.broker.list': 'ec2-3-209-146-134.compute-1.amazonaws.com, ec2-18-205-11-135.compute-1.amazonaws.com, ec2-3-209-201-239.compute-1.amazonaws.com'
  }, {}, {
    topic: target
  });
```

Point towards the correct PostGres Database:

In consumer.py
```
conn = psycopg2.connect(user="laitcl",
                             password=passwordstring,
                             host="10.0.0.12",
                             port="5432",
                             database="testpython")
```

In ChromeExtension/Flask/App.py
```
with open ('PostgresPass.txt', 'r') as file:
    passwordstring = file.readline().split("\n")[0]
try:
    conn = psycopg2.connect(user = "laitcl",
                                 password = passwordstring,
                                 host = "ec2-3-80-4-183.compute-1.amazonaws.com",
                                 port = "5432",
                                 database = "testpython")
```

Point towards your own pusher account:

In ChromeExtension/Flask/App.py
```
with open ('pusherinfo.txt', 'r') as file:
    secretstring = file.readline().split("\n")[0]
    pusher = Pusher(
        app_id='811964',
        key='114fb576b66e1ffc4165',
        secret=secretstring,
        cluster='mt1',
        ssl=True
    )
```

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisties

This code uses different computational clusters to acquire, send, and analyze messages. The following servers must be installed

Kafka brokers: Install Zookeeper and Kafka on 2 or more Kafka brokers to allocate acquired messages for analysis

Kafka producers: Install Zookeeper and NodeJS on at least 3 Twitch bot clusters to acquire Twitch TV messages. Must also own a Twitch.TV account.

Kafka consumers: Install Zookeeper, Kafka, and python on 1 or more Kafka consumers to analyze messages and output to PostgreSQL.

PostgreSQL Server: Install PostgreSQL on 1 server to receive message analysis from Kafka consumer.

UI Server: Install Python on 1 host server (can be same server as PostgreSQL) to be able to use Flask to host website for chrome extension.


Documentation for installing Kafka can be found [here](https://github.com/InsightDataScience/data-engineering-ecosystem/wiki/Kafka). Installation for Zookeeper can be found [here](https://github.com/InsightDataScience/data-engineering-ecosystem/wiki/zookeeper).

Installation instructions for PostgreSQL can be found [here](https://www.postgresql.org/download/).

### Installing Packages

The following are the dependencies for this tool

Python for consumers, UI, and machine learning model
```
pip install keras
pip install kafka-python
pip install tensorflow
pip install json
pip install nltk
pip install psycopg2
```

Download punkt from nltk for machine learning model
```
import nltk
nltk.download('punkt')
```

Install Node JS for producers
```
sudo apt install nodejs
sudo apt install npm
```

NodeJS modules for producers
```
npm install tmi.js
npm install node-rdkafka
```

## Running the tool

To run this tool:

1. **Turn on all servers** - To enable to use of servers
2. **Start Zookeeper** - Start Zookeeper on all Kafka brokers, Consumers, and Producers to allow for information to be transferred between the servers.
3. **Start Kafka** - Start Kafka on all Kafka brokers and consumers to allow information to be communicated between the two.
4. **Modify credentials.js** - Change `Twitchbot/credentials.js` include all channels that you would like to monitor. This tool is designed to ingest messages from 50 or more channels.
5. **Distribute the channels list** - Distribute list to Kafka Consumers and Producers using ipython notebooks `Twitchbot/ChannelListWriter.ipynb` and `CredentialsWriter.ipynb`. Number of nodes can be specified in top cell. Bottom cell should be modified so that secure copy statements are copied to designated channels.
6. **Start Producers** - Producers can be started by running `node Twitchbot/chatbot_Lai.js`
7. **Start Consumers** - Consumers can be started by running `python consumer.py`
8. **Run Flask Server** - Server can be started by running `python ChromeExtension/Flask/App.py`
9. **Add Chrome Extension** - By going to `chrome://extensions`, developer mode, and unpacking ChromeExtension/extension.
10. **View output** - Go to a twitch.tv Channel, and click on Chrome extension popup button to view output.

## Authors

* **Lawrence Lai** - [GitHub: laitcl](https://github.com/laitcl/)

## Acknowledgments

This project acknowledges [Insight Data Science's Data Engineering Program](https://www.insightdataengineering.com/) for the guidance.
