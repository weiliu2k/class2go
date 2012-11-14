/***
 * Applies function to a given element with id safely
 **/
function tryAccessElem(elemId, fun) {
	if (elemId) {
		elem = document.getElementById(elemId);
		if (elem) {
			fun(elem);
		}
	}
}
function createDiv(elemId, className) {
	divElem = document.createElement("div");
	divElem.id = elemId;
	divElem.className = className;
	return divElem;
}
/***
 * Returns a string of the given padded length
 **/
function pad(number, length) {
	var str = "" + number;
	var padding = "";
	if (str.length < length) {
		padding = (str.length-length) * "0";
	}
	return padding+str;
}

/***
 * Quizzes can be enabled/disabled entirely:
 **/
var enableQuizzes = true;
function toggleQuizzes(elemId) {
	console.log("Found", elemId);
	var elem = document.getElementById(elemId)
		if (enableQuizzes) {
			elem.innerHTML = "SQuizzes";
		}
		else {
			elem.innerHTML = "HQuizzes";
		}
	enableQuizzes = !enableQuizzes;
}

/***
 * A QuizQn is an instance of a cueData, with onStartFun and onEndFun
 * defined to reveal/hide the quiz as required.
 **/
function QuizQn(start, end, html) {
	this.start = start;
	this.end = end;
	this.html = html;
}

QuizQn.prototype.onStartFun = function(video, overlayElemId) {
	var overlayElem = document.getElementById(overlayElemId);
	if (enableQuizzes) {
		video.pause();
		overlayElem.innerHTML = this.html;
		overlayElem.style.visibility = "visible";
	}
	else {
		overlayElem.style.visibility = "hidden";
	}
};

QuizQn.prototype.onEndFun = function(video, overlayElemId) {
	var overlayElem = document.getElementById(overlayElemId);
	overlayElem.style.visibility = "hidden";
};

/***
 * Defines a video object with associated overlay layer (optional) element.
 * The overlay layer element receives callbacks from the video object.
 *
 * 		-- video: Accepts a popcorn video object.
 * 		-- overlayElemId: Id of the overlay element.
 **/
var isProgressBarMouseDown = false;
var areCaptionsEnabled = true;
function VideoPlayer(video, overlayElemId) {
	this.overlayElemId = overlayElemId;
	this.markerContainer = "marker-bar";
	this.cueData;
	/***
	 * Add cued events to the overlayElement.
	 * 		-- cueData is a list of objects with the following fields:
	 * 				-- start: time in seconds
	 * 				-- end: time in seconds
	 * 				-- onStartFun: function called on start of cue
	 * 				-- onEndFun: function called on end of cue
	 * 						  -- each Fun accepts two arguments, the video object
	 * 						     and the overlayElemId.
	 **/
	this.addCuesToVideo = function(cueData) {
		if (cueData) {
			this.cueData = cueData;
			for (var i = 0; i < cueData.length; i++) {
				(function(i) {
					var cueDatum = cueData[i];
					video.code({
						start: cueDatum.start,
						end: cueDatum.end,
						onStart: function(options) {
							cueDatum.onStartFun(video, overlayElemId);
						},
						onEnd: function(options) {
							cueDatum.onEndFun(video, overlayElemId);
						}
					});
				})(i);
			}
		}
	};
	/***
	 * Add subtitles to the video:
	 * 	-NOTE: popcorn.js has a native sbv support which I'm not sure about.
	 **/
	this.addSubtitlesToVideo = function(subtitles, subtitlesId) {
		if (subtitles) {
			for (var i = 0; i < subtitles.length; i++) {
				(function(i) {
					var subtitle = subtitles[i];
					video.text({
						start: subtitle.start,
						end: subtitle.end,
						text: subtitle.caption,
						multiline: true,
					});
				})(i);
			}
		}
	};

	this.volume = 1.0; //Set to max volume by default
	/***
	 * Adds controls to the video player.
	 * Should supply the root name of the control element.
	 * Will dynamically create the control elements.
	 *
	 * If the element does not exist, no callback is generated for that control.
	 **/
	this.addControls = function(controlElemId) {
		if (controlElemId) {
			var controlElem = document.getElementById(controlElemId);

			//Add callbacks for pause/play controls
			var playElem = createDiv("play", "play");
			playElem.innerHTML = '<i class="icon-play icon-white"></i>';
			playElem.addEventListener("click", function() {
				if (video.paused()) {
					video.play();
				} else {
					video.pause();
				}
			},false);
			controlElem.appendChild(playElem);
			video.on("play", function() {
				playElem.innerHTML = '<i class="icon-pause icon-white"></i>';
			});
			video.on("playing", function() {
				playElem.innerHTML = '<i class="icon-pause icon-white"></i>';
			});
			video.on("pause", function() {
				playElem.innerHTML = '<i class="icon-play icon-white"></i>';
			});

			//Add callback for stop control
			var stopElem = createDiv("stop", "stop");
			stopElem.innerHTML= '<i class="icon-stop icon-white"></i>';
			stopElem.addEventListener("click", function() {
				video.pause(0);
			},false);
			controlElem.appendChild(stopElem);

			//Add subtitleing support (warning: only for HTML5 youtube player)
			var subtitleElem = createDiv("subtitle", "subtitle");
			subtitleElem.innerHTML = 'HCaption';
			subtitleElem.addEventListener("click", function() {
				var subtitleTextElem = document.getElementById("text");
				if (subtitleTextElem) {
					if (subtitleTextElem.style.visibility == "visible") {
						console.log("hiding subtitles")
						subtitleTextElem.style.visibility = "hidden";
						subtitleElem.innerHTML = 'SCaption';
					}
					else {
						console.log("showing subtitles")
						subtitleTextElem.style.visibility = "visible";
						subtitleElem.innerHTML = 'HCaption';
					}
				}
			});
			controlElem.appendChild(subtitleElem);

			//Add volume controls
			var muteElem = createDiv("mute", "mute");
			muteElem.innerHTML = '<i class="icon-volume-up icon-white"></i>';
			muteElem.muted = false;
			muteElem.addEventListener("click", function() {
				console.log(muteElem.muted)
				if (muteElem.muted) {
					video.unmute();
					//video.volume(this.volume);
					muteElem.muted = false;
				}
				else {
					video.mute();
					muteElem.muted = true;
				}
			}, false);

			video.on("volumechange", function() {
				if (video.volume() == 0) {
					muteElem.innerHTML = '<i class="icon-volume-off icon-white"></i>';
				}
				else if (video.volume() < 0.5) {
					muteElem.innerHTML = '<i class="icon-volume-down icon-white"></i>';
				}
				else {
					muteElem.innerHTML = '<i class="icon-volume-up icon-white"></i>';
				}
			});

			var volumeBoxElem = createDiv("volume-box", "volume-box");
			var volumeSliderElem = createDiv("volume-slider", "volume-slider");
			controlElem.appendChild(volumeBoxElem);
			volumeBoxElem.appendChild(volumeSliderElem);
			volumeBoxElem.appendChild(muteElem);

			//Add time display:
			var timeElem = createDiv("time", "time");
			timeElem.innerHTML='00:00:00';
			controlElem.appendChild(timeElem);

			video.on("timeupdate", function(e) {
				var maxTime = video.duration();
				var time = video.currentTime();
				var percentage = (time / maxTime) * 100.0;
				timeBarElem.style.width = percentage + "%";

				time = Math.round(time);
				var seconds = time % 60;
				var timeMin = (time - seconds) / 60;
				var minutes = timeMin % 60;
				var hours = (timeMin - minutes) / 60;
				timeElem.innerHTML = pad(hours,2) + ":" + pad(minutes, 2) + ":" + pad(seconds,2);
			},false);

			//Add progress bar controls
			var progressBarElemId = "progress-bar";
			var timeBarElemId = "time-bar";
			var progressBarElem = createDiv(progressBarElemId, "progress-bar");
			var timeBarElem = createDiv(timeBarElemId, "time-bar");
			controlElem.appendChild(progressBarElem);
			progressBarElem.appendChild(timeBarElem);
			progressBarElem.addEventListener("mousedown", function(e) {
				isProgressBarMouseDown = true;
				seekTo(e.pageX, progressBarElemId, timeBarElemId,video);
			}, false);
			document.addEventListener("mouseup", function(e) {
				if (isProgressBarMouseDown) {
					isProgressBarMouseDown = false;
					seekTo(e.pageX, progressBarElemId, timeBarElemId,video);
				}
			}, false);
			document.addEventListener("mousemove", function(e) {
				if (isProgressBarMouseDown) {
					seekTo(e.pageX, progressBarElemId, timeBarElemId,video);
				}
			}, false);


			var cueContainer = createDiv(this.markerContainer, this.markerContainer);
			progressBarElem.appendChild(cueContainer);
			//Add visual indicators for quizzes:
			if (this.cueData) {
				var cueData = this.cueData;
				video.on("loadedmetadata", function() {
					var maxTime = video.duration();
					for (var i = 0; i < cueData.length; i++) {
						(function(i) {
							var cueDatum = (cueData)[i];
							var start = cueDatum.start;
							var cueElemId ="cue"+i;
							var cueElem = createDiv(cueElemId, "marker");
							var percentage = 100.0 * start / maxTime;
							cueElem.style.left = percentage + "%";
							cueElem.style.z_index = "" + (2+i);
							cueElem.start = start;
							cueContainer.appendChild(cueElem);

							var clickListener = (function(elem) {
								return function(e) {
									console.log(elem.id + " was pressed ");
									video.pause(elem.start);
								}
							})(cueElem);

							document.getElementById(cueElemId).addEventListener("click", clickListener);
						})(i);
					}
				});
			}
		}//if controlElemId
	} //if controls
} //VideoPlayer

VideoPlayer.prototype.hideOverlay = function() {
	tryAccessElem(this.overlayElemId, function(elem) {
		elem.style.visibility = "hidden";
	});
	tryAccessElem(this.markerContainer, function(elem) {
		elem.style.visibility = "hidden";
	});
};
VideoPlayer.prototype.showOverlay = function() {
	tryAccessElem(this.overlayElemId, function(elem) {
		elem.style.visibility = "show";
	});
	tryAccessElem(this.markerContainer, function(elem) {
		elem.style.visibility = "show";
	});
};

/***
 * Functions to support seek on the page
 **/
function seekTo(xPos, progressBarElemId, timeBarElemId,video) {
	progressBarElemId = "#" + progressBarElemId;
	var width = $(progressBarElemId).width();
	var originPos = $(progressBarElemId).offset().left;
	var maxTime = video.duration();//returns NaN if duration not available yet
	var newWidth = Math.max(Math.min(xPos - originPos, width), 0);
	var percentage = 100.0 * (xPos - originPos)/ width;
	if (percentage > 100) {
		percentage= 100;
	}
	if (percentage < 0) {
		percentage= 0;
	}
	if (maxTime) {
		var time = percentage * maxTime / 100;
		video.pause(time);
		var time = video.currentTime();
		var percentage = (time / maxTime) * 100.0;
		document.getElementById(timeBarElemId).style.width = percentage + "%";
	}
}

