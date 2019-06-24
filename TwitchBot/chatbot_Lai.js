const tmi = require('tmi.js');
var credentials = require('./credentials');
var Kafka = require('node-rdkafka');

// Setup Writefile
const fs = require('fs');
const writepath='messagelog.csv'

// Define configuration options
const opts = credentials.opts;

// Create a client with our options
const client = new tmi.client(opts);

// Register our event handlers (defined below)
client.on('message', onMessageHandler);
client.on('connected', onConnectedHandler);

// Connect to Twitch:
client.connect();

// Called every time a message comes in
function onMessageHandler (target, context, msg, self) {
  if (self) { return; } // Ignore messages from the bot
  //console.log(`* Target ${target} Context ${context} message ${msg} self${self}`);
  writemessageKafka(target, msg)
}

// Function called when the "dice" command is issued
function rollDice () {
  const sides = 6;
  return Math.floor(Math.random() * sides) + 1;
}

// Function called whenever line of text should be outputted
function writemessageKafka(target, msg) {
  datestring = fulldate()
  target = target.substr(1);
  console.log(target)
  outputmessage = datestring +target+','+ msg+ '\r\n'
  //console.log(outputmessage)
  //  Outputs to Kafka and check status of output
  // Kafka Producer
  // This call returns a new writable stream to our topic 'topic-name'
  var stream = Kafka.Producer.createWriteStream({
    'metadata.broker.list': 'ec2-3-209-146-134.compute-1.amazonaws.com, ec2-18-205-11-135.compute-1.amazonaws.com, ec2-3-209-201-239.compute-1.amazonaws.com'
  }, {}, {
    topic: target
  });

  var queuedSuccess = stream.write(Buffer.from(outputmessage));
    if (queuedSuccess) {
      console.log('Message queued on ' + datestring);
    } else {
      // Note that this only tells us if the stream's queue is full,
      // it does NOT tell us if the message got to Kafka!  See below...
      console.log('Too many messages in our queue already');
    }

  // NOTE: MAKE SURE TO LISTEN TO THIS IF YOU WANT THE STREAM TO BE DURABLE
  // Otherwise, any error will bubble up as an uncaught exception.
  stream.on('error', function (err) {
    // Here's where we'll know if something went wrong sending to Kafka
    console.error('Error in our kafka stream');
    console.error(err);
  })
}

function writemessageCSV(target, msg) {
//  Output to CSV components
  datestring = fulldate()
  outputmessage = datestring +target+','+ msg+ '\r\n'
//  fs.appendFile(writepath, outputmessage, (err) => {
//    // In case of a error throw err.
//    if (err) throw err;
//})
}

//Get date
function fulldate() {
  var d = new Date();
  var year = d.getFullYear();
  var month = d.getMonth()+1;
  var day = d.getDate();
  var hour = d.getHours();
  var minute = d.getMinutes();
  var seconds = d.getSeconds();
  var mseconds = d.getMilliseconds();
  var full_date = year+ "-"+month+"-"+day+"_"+hour + ":" + minute + ":" + seconds + ":" + mseconds + ",";
  return full_date
}

// Called every time the bot connects to Twitch chat
function onConnectedHandler (addr, port) {
  console.log(`* Connected to ${addr}:${port}`);
}
