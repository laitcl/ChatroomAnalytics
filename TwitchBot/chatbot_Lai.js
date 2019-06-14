const tmi = require('tmi.js');

// Setup Writefile
const fs = require('fs');
const writepath='messagelog.csv'

// Define configuration options
const opts = {
  identity: {
    username: "Redacted",
    password: "Redacted"
  },
  channels: [
    "laitcl",
  ]
};

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
  writemessage(target, msg)
}

// Function called when the "dice" command is issued
function rollDice () {
  const sides = 6;
  return Math.floor(Math.random() * sides) + 1;
}

// Function called whenever line of text should be outputted to CSV
function writemessage(target, msg) {
  datestring = fulldate()
  fs.appendFile(writepath, datestring +target+','+ msg+ '\r\n', (err) => {
    // In case of a error throw err.
    if (err) throw err;
})
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
