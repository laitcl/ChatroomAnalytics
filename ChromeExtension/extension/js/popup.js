//get name of current tab

//var channelname = window.prompt("Enter channel name: ");
//writeTextFile(channelname)

//function to write to file
function writeTextFile(channelname)
{
  var txtFile = new File([""], "channel.txt");
  txtFile.WriteLine(channelname);
  txtFile.close();
}


// function setup() {
	// var x = document.createElement("INPUT");
    // x.setAttribute("type", "button");
	
	// let userinput = select('#userinput')
	// user.
// }





// var query = {active:true,currentWindow:true};
// chrome.tabs.query(query, callback);
// function callback(tabs) {
  // var currentTab = tabs[0];
  // var channelname = currentTab["url"].split("/")[3];
  // console.log(channelname)
  // writeTextFile("channel.txt", channelname)
  // console.log(2)








// };



	
//plotly components
// var data = [
  // {
    // x: ["2013-10-04 22:23:00", "2013-11-04 22:23:00", "2013-12-04 22:23:00"],
    // y: [1, 3, 6],
    // type: "scatter"
  // }
// ];
// var graphOptions = {filename: "date-axes", fileopt: "overwrite"};
// plotly.plot(data, graphOptions, function (err, msg) {
    // console.log(msg);
// });
