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
 * Prints out the time given time in seconds
 ***/
function printTime(time) {
	time = Math.round(time);
	var seconds = time % 60;
	var timeMin = (time - seconds) / 60;
	var minutes = timeMin % 60;
	var hours = (timeMin - minutes) / 60;
	return pad(hours,2) + ":" + pad(minutes, 2) + ":" + pad(seconds,2);
}

/***
 * Quizzes can be enabled/disabled entirely:
 **/
var enableQuizzes = true;
function toggleQuizzes(elem) {
	if (enableQuizzes) {
		$(elem).html("Squizzes");
	}
	else {
		$(elem).html("Hquizzes");
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

QuizQn.prototype.onStartFun = function(video, overlayElem) {
	if (enableQuizzes) {
		video.pause();
		$(overlayElem).html(this.html).css("visibility", "visible");
	}
	else {
		$(overlayElem).html(this.html).css("visibility", "hidden");
	}
};

QuizQn.prototype.onEndFun = function(video, overlayElem) {
	$(overlayElem).css("visibility", "hidden");
};

/***
 * Defines a video object with associated overlay layer (optional) element.
 * The overlay layer element receives callbacks from the video object.
 *
 * 		-- video: Accepts a popcorn video object.
 * 		-- overlayElem:  of the overlay element.
 **/
var isProgressBarMouseDown = false;
var areSubtitlesEnabled = true;
function VideoPlayer(video, overlayElem) {
	this.overlayElem = overlayElem;
	this.markerContainer = "#marker-bar";
	this.cueData;
	/***
	 * Add cued events to the overlayElement.
	 * 		-- cueData is a list of objects with the following fields:
	 * 				-- start: time in seconds
	 * 				-- end: time in seconds
	 * 				-- onStartFun: function called on start of cue
	 * 				-- onEndFun: function called on end of cue
	 * 						  -- each Fun accepts two arguments, the video object
	 * 						     and the overlayElem.
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
							cueDatum.onStartFun(video, overlayElem);
						},
						onEnd: function(options) {
							cueDatum.onEndFun(video, overlayElem);
						}
					});
				})(i);
			}
		}
	};
	/***
	 * Add subtitles to the video:
	 **/
	this.addSubtitlesToVideo = function(subtitleFile, subtitlesElem) {
		$.getJSON(subtitleFile, function(subtitles) {
			if (subtitles) {
				for (var i = 0; i < subtitles.length; i++) {
					(function(i) {
						var subtitle = subtitles[i];
						video.code({
							start: subtitle.start,
							end: subtitle.end,
							onStart: function() {
								$(subtitlesElem).html(subtitle.subtitle);
							},
							onEnd: function() {},
						});
					})(i);
				}
			}
		});
	};
	/***
	 * Adds scrolling gallery of thumbnails
	 ***/
	this.addThumbnailGallery = function(img, gallery, rootD) {
		generateThumbnails(img, gallery, rootD, function(thumbnails) {
			for (var i = 0; i < thumbnails.length; i++) {
				(function(i) {
					var item = thumbnails[i];
					var endTime = video.duration();
					if (i < thumbnails.length - 1) {
						endTime = thumbnails[i+1].time;
					}
					video.code({
						start: item.time,
						end: endTime,
						onStart: function() {
							scrollTo(gallery, thumbnails, item.count);
							$(item.id).addClass("gallery-item-active");
						},
						onEnd: function() {
							$(item.id).removeClass("gallery-item-active");
						},
					});
					$(item.id).click(function() {
						video.pause(item.time);
					});
				})(i);
			}
		});
	};

	/***
	 * Adds scrolling transcript
	 ***/
	this.addTranscriptGallery = function(subtitleFile, gallery) {
		generateTranscripts(subtitleFile, gallery, function(subtitles) {
			for (var i = 0; i < subtitles.length; i++) {
				(function(i) {
					var item = subtitles[i];
					video.code({
						start: item.start,
						end: item.end,
						onStart: function() {
							scrollTo(gallery, subtitles, item.count);
							$(item.id).addClass("transcript-item-active");
						},
						onEnd: function() {
							$(item.id).removeClass("transcript-item-active");
						},
					});
					$(item.id).click(function() {
						video.pause(item.start);
					});
				})(i);
			}
		});
	};

	this.volume = 1.0; //Set to max volume by default
	/***
	 * Adds controls to the video player.
	 * Should supply the root name of the control element.
	 * Will dynamically create the control elements.
	 *
	 * If the element does not exist, no callback is generated for that control.
	 **/
	this.addControls = function(controlElem) {
		if (controlElem) {
			//Add callbacks for pause/play controls
			var playElem = "#play";
			$('<div/>', {
				id: "play",
				class: "controls btn btn-inverse controls-left",
				text: '<i class="icon-play icon-white"></i>',
				click: function() {
					if (video.paused()) {
						video.play();
					} else {
						video.pause();
					}},}
			 ).appendTo(controlElem);
			video.on("play", function() {
				$(playElem).html('<i class="icon-pause icon-white"></i>');
			});
			video.on("playing", function() {
				$(playElem).html =('<i class="icon-pause icon-white"></i>');
			});
			video.on("pause", function() {
				$(playElem).html =('<i class="icon-play icon-white"></i>');
			});

			//Add volume controls
			var muteElem = "#mute";
			$('<div/>', {
				id: "mute",
				class: "controls btn btn-inverse controls-right",
				text: '<i class="icon-volume-up icon-white"></i>',
				click: function() {
					if ($(muteElem).attr("muted")) {
						video.unmute();
						$(muteElem).attr("muted", false);
					}
					else {
						video.mute();
						$(muteElem).attr("muted", true);
					}}}
			 ).appendTo(controlElem);

			video.on("volumechange", function() {
				if (video.volume() == 0) {
					$(muteElem).html('<i class="icon-volume-off icon-white"></i>');
				}
				else if (video.volume() < 0.5) {
					$(muteElem).html('<i class="icon-volume-down icon-white"></i>');
				}
				else {
					$(muteElem).html('<i class="icon-volume-up icon-white"></i>');
				}
			});


			var volumeBoxElem = createDiv("volume-box", "volume-box");
			var volumeSliderElem = createDiv("volume-slider", "volume-slider");
			controlElem.appendChild(volumeBoxElem);
			volumeBoxElem.appendChild(volumeSliderElem);
			volumeBoxElem.appendChild(muteElem);

			$(volumeSlider).slider({
				value: 1,
				orientation: "horizontal",
				range: "min",
				max: 1,
				step: 0.05,
				animate: true,
				slide:function(e,ui){
					video.volume(ui.value);
					$(volumeSlider).attr("volume", ui.value);
				}
			});


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
			var progressBarElem = "progress-bar";
			var timeBarElem = "time-bar";
			var progressBarElem = createDiv(progressBarElem, "progress-bar");
			var timeBarElem = createDiv(timeBarElem, "time-bar");
			controlElem.appendChild(progressBarElem);
			progressBarElem.appendChild(timeBarElem);
			progressBarElem.addEventListener("mousedown", function(e) {
				isProgressBarMouseDown = true;
				seekTo(e.pageX, progressBarElem, timeBarElem,video);
			}, false);
			document.addEventListener("mouseup", function(e) {
				if (isProgressBarMouseDown) {
					isProgressBarMouseDown = false;
					seekTo(e.pageX, progressBarElem, timeBarElem,video);
				}
			}, false);
			document.addEventListener("mousemove", function(e) {
				if (isProgressBarMouseDown) {
					seekTo(e.pageX, progressBarElem, timeBarElem,video);
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
							var cueElem ="cue"+i;
							var cueElem = createDiv(cueElem, "marker");
							var percentage = 100.0 * start / maxTime;
							cueElem.style.left = percentage + "%";
							cueElem.style.z_index = "" + (2+i);
							cueElem.start = start;
							cueContainer.appendChild(cueElem);

							var clickListener = (function(elem) {
								return function(e) {
									video.pause(elem.start);
								}
							})(cueElem);

							document.getElementBy(cueElem).addEventListener("click", clickListener);
						})(i);
					}
				});
			}
		}//if controlElem
	} //if controls
} //VideoPlayer

VideoPlayer.prototype.hideOverlay = function() {
	$(this.overlayElem).css("visibility", "hidden");
	$(this.markerContainer).css("visibility", "hidden");
};
VideoPlayer.prototype.showOverlay = function() {
	$(this.overlayElem).css("visibility", "visible");
	$(this.markerContainer).css("visibility", "visible");
};

/***
 * Functions to support seek on the page
 **/
function seekTo(xPos, progressBarElem, timeBarElem,video) {
	progressBarElem = "#" + progressBarElem;
	var width = $(progressBarElem).width();
	var originPos = $(progressBarElem).offset().left;
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
		document.getElementBy(timeBarElem).style.width = percentage + "%";
	}
}

