
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = 0;
    
    //receive details from server
    socket.on('newdata', function(msg) {
        console.log(msg)
        console.log(msg.hour + ":" + msg.minute + ":" + msg.second);
        console.log("hello");        
        document.getElementById("log").innerHTML = (msg.hour + ":" + msg.minute + ":" + msg.second+ "-"+ msg.status);
    });

});

var slider = document.getElementById("myRange");
var output = document.getElementById("value");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
}
