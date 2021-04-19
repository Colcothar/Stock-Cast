var slider = document.getElementById("myRange");
var output = document.getElementById("value");
output.innerHTML = slider.value;


//this code updates the slider value on the basic predictor page

slider.oninput = function() { 
  output.innerHTML = this.value;
  
}




