var eBars = document.querySelectorAll(".e path");
var threeBars = document.querySelectorAll(".three path");
var cars = document.querySelectorAll(".car image");
var index = cars.length-1;
var duration = 5;
var date = new Date();
//Four months 26 days late when I changed this
// 3 days more
var targetDate = new Date("April 31, 2018 17:00:00");
var dateText = document.querySelector("text");


TweenMax.set(".tesla path", {drawSVG: "100% 100%"});
TweenMax.set(".model path", {drawSVG: "0% 0%", opacity:1});

TweenMax.to("svg",1,{opacity:1,ease:Power3.easeOut});


function model3() {
		TweenMax.staggerTo(".tesla path", 1, {drawSVG: "100% 100%",fillOpacity: 0,ease: Power2.easeOut}, .11);
		TweenMax.staggerTo(".model path", 1, {delay: .3,fillOpacity: 1,ease: Power2.easeOut}, .11);
		TweenMax.staggerFromTo(".model path", 2, {delay: .3,drawSVG: "0% 0%"}, {drawSVG: "0% 100%",ease: Quint.easeOut}, .11);
		for (var i = 0; i < eBars.length; i++) {
				var eBar = eBars[i];
				var threeBar = threeBars[i];
				TweenMax.to(eBar, 1, {delay: i * .05, morphSVG: threeBar, ease: Power4.easeInOut});
		}
		TweenMax.delayedCall(duration, tesla);
}

function tesla() {
		TweenMax.staggerTo(".tesla path", 1, {delay: .3,fillOpacity: 1,ease: Power2.easeOut}, -.11);
		TweenMax.staggerTo(".model path", 1, {drawSVG: "100% 100%",fillOpacity: 0,ease: Power2.easeOut}, -.11);
		TweenMax.staggerFromTo(".tesla path", 2, {delay: 0.3,drawSVG: "100% 100%"}, {drawSVG: "0% 100%",ease: Quint.easeOut}, -.11);
		for (var i = 0; i < eBars.length; i++) {
				var eBar = eBars[i];var threeBar = threeBars[i];
				TweenMax.to(eBar, 1, {delay: i * .05, morphSVG: eBar, ease: Power4.easeInOut});
		}
		TweenMax.delayedCall(duration, model3);
}

function cycle() {
		if (index <= 0) {index = cars.length - 1;TweenMax.to(cars[index], 2, {    autoAlpha: 1,    ease: Power2.easeOut});TweenMax.set(cars, {    autoAlpha: 1,    delay: 2});
		} else {TweenMax.to(cars[index], 2, {
						autoAlpha: 0,
						ease: Power2.easeOut
				});
				index--;
		}
		TweenMax.delayedCall(duration, cycle);
}

TweenMax.delayedCall(duration,model3);
TweenMax.delayedCall(duration,cycle);

function getDays(currentDate,targetDate)
{
	var targetYear=currentDate.getFullYear();
       var dayCount=(targetDate-currentDate)/(1000*60*60*24);
    return Math.round(dayCount); 
}

dateText.textContent = "Delivered April 31, 2018!";
