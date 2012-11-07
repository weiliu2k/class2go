document.cancelFullScreen = document.webkitExitFullscreen || document.mozCancelFullScreen || document.exitFullscreen;

var elem = document.querySelector(document.webkitExitFullscreen ? "#fs" : "#fs-container");

document.addEventListener('keydown', function(e) {
	switch (e.keyCode) {
		case 13: // ENTER. ESC should also take you out of fullscreen by default.
			e.preventDefault();
			document.cancelFullScreen(); // explicitly go out of fs.
			break;
		case 70: // f
			enterFullscreen();
			break;
	}
}, false);

function toggleFS(el) {
	if (el.webkitEnterFullScreen) {
		el.webkitEnterFullScreen();
	} else {
		if (el.mozRequestFullScreen) {
			el.mozRequestFullScreen();
		} else {
			el.requestFullscreen();
		}
	}

	el.ondblclick = exitFullscreen;
}

function onFullScreenEnter() {
	console.log("Entered fullscreen!");
	elem.onwebkitfullscreenchange = onFullScreenExit;
	elem.onmozfullscreenchange = onFullScreenExit;
};

// Called whenever the browser exits fullscreen.
function onFullScreenExit() {
	console.log("Exited fullscreen!");
};

// Note: FF nightly needs about:config full-screen-api.enabled set to true.
function enterFullscreen() {
	console.log("enterFullscreen() was activated");
	elem.onwebkitfullscreenchange = onFullScreenEnter;
	elem.onmozfullscreenchange = onFullScreenEnter;
	elem.onfullscreenchange = onFullScreenEnter;
	if (elem.webkitRequestFullscreen) {
		elem.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
	} else {
		if (elem.mozRequestFullScreen) {
			elem.mozRequestFullScreen();
		} else {
			elem.requestFullscreen();
		}
	}
	document.getElementById('toggle-fs').onclick = exitFullscreen;
}

function exitFullscreen() {
	console.log("exitFullscreen()");
	document.cancelFullScreen();
	document.getElementById('toggle-fs').onclick = enterFullscreen;
}

