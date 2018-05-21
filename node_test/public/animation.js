

//var c = document.getElementById('animation'); // 1920 x 1080 canvas
var c = document.querySelector("#animation");
c.width = 1920;
c.height = 1080;

var x = c.getContext('2d'); // 2D context for canvas
var S = Math.sin;

var time = 0;
var frame = 0;
function u(t) {
	t*=3;
	c.width |= 1;
	x.linewidth = 3;
	for (i = 1; i < 50; i++) {
		x.beginPath();
		x.arc(480+10*i,540,50+(i*10),t+(i*3)+S(t),t+(i*3)+1);
		x.stroke();
	}
}

// document.body.innerHTML = "<h1>Today is: " + new Date() + "</h1>";

var FPS = 60;

function loop() {
	if(true) {
		requestAnimationFrame(loop);
	}
	time = frame/FPS
	if(time * FPS | 0 == frame - 1) {
		time += 0.000001;
	}
	frame++;

	u(time);
}

loop();

//window.setInterval(function(){
//	animation((new Date).getTime());
//}, 166)

