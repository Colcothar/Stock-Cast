$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = 0;
    var x = document.getElementById("button")
    
    //receive details from server
    socket.on('newdata', function(msg) {
        console.log(msg)
        console.log(msg.hour + ":" + msg.minute + ":" + msg.second);
            
        document.getElementById("log").innerHTML = (msg.hour + ":" + msg.minute + ":" + msg.second+ "-"+ msg.status); //update the box on the screen with the new timer value
        if (msg.status == "Complete"){ 
   
            x.style.display = "block"; //when the training has finished display the "GO" box
        }
  
      });
  
  });