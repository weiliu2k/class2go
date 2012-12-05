var expandContainer = "#gallery-container";
var expandBar = "#gallery-sidebar";
var expandCtrl = "#gallery-expand";
var collapseCtrl = "#gallery-collapse";
var playerCtrls = "#player-controls";
var playerContainer = "#player";
var videoContainer = "#video";

var withSidebar = true;

/***
 * Sidebar initialization. Should be called before any resize functions
 ***/
function initializeSidebar() {
	//Attributes used to ensure correct sizing of player
	$(playerContainer).attr("minHeight", $(playerContainer).height());
	$(playerContainer).attr("sidebarWidth", $(expandContainer).width());
	$(playerContainer).attr("aspectRatio", $(playerContainer).height()*1.0/$(playerContainer).width());

	$(expandCtrl).hide();
	expandFn = (function(playerContainer, expandCtrl) {
		return function() {
			withSidebar = true;

			//Reveal sidebar
			$(playerCtrls).css('border-top-right-radius', '0px');
			$(expandContainer).show();
			$(expandBar).animate({width:$(playerContainer).attr("sidebarWidth")}, 700, "swing");
			resizePlayer();

			//Swap expand/collapse controls
			$(expandCtrl).hide();
			$(collapseCtrl).show();
		}
	})(playerContainer, expandCtrl)

	$(expandCtrl).click(expandFn);
	collapseFn = (function(playerContainer, expandCtrl) {
		return function() {
			withSidebar = false;

			//Hide sidebar
			$(expandBar).animate({width:0}, 700, "swing", function() {
				$(expandContainer).css({display:"none"});
				$(playerCtrls).css('border-top-right-radius', '3px');
			});
			resizePlayer();

			//Swap expand/collapse controls
			$(expandCtrl).show();
			$(collapseCtrl).hide();
		}
	})(playerContainer, expandCtrl)

	$(collapseCtrl).click(collapseFn);

	/***
	 * Gallery controls
	 ***/
	$("#toggle-thumbnail").click(function() {
		$("#gallery").css("display", "block");
		$("#transcript").css("display", "none");
		$("#toggle-thumbnail").css("display", "none");
		$("#toggle-transcript").css("display", "block");
	});

	$("#toggle-transcript").click(function() {
		$("#gallery").css("display", "none");
		$("#transcript").css("display", "block");
		$("#toggle-thumbnail").css("display", "block");
		$("#toggle-transcript").css("display", "none");
	});
}

/***
 * Global functions to resize player
 ***/
function computeHeight(playerContainer, withSidebar) {
	var width = $(playerContainer).width();
	if (!withSidebar) {
		width = width + parseInt($(playerContainer).attr("sidebarWidth"), 10);
	}
	var newHeight = Math.round($(playerContainer).attr("aspectRatio")*width);
	return Math.min($(window).height(), newHeight);
}

function resizePlayer() {
	var newHeight = computeHeight(playerContainer, withSidebar);
	if (isFullscreen || newHeight >= $(playerContainer).attr("minHeight")) {
		$(videoContainer).animate({opacity:0},200,"linear", function() {
				$(playerContainer).animate({height:newHeight},500,"swing", function() {
					$(videoContainer).animate({opacity:1},200,"linear");
				});
		});
	}
}


/***
 * Creates divs according to the type and adds them as children to parentDiv.
 *
 * Returns an array of div id in form #id for jQuery
 ***/
function generateThumbnails(manifestFile, parentDiv, rootDir, callback) {
	var count = 0;
	var padding = parseInt($(parentDiv).css('padding-top'),10);
	var height = 0;
	var thumbnails = new Array();
	var imgs = $.getJSON(manifestFile, function(imgs) {
		for (var key in imgs) {
			var img = imgs[key];
			var id = parentDiv + "-child-" + count;
			var thumbnail = {"id": id, "time":key, "count": count};
			$("<div/>", {
				id : thumbnail.id.substring(1),
				class : "gallery-item",
				html : "<img src='" + rootDir + img.imgsrc + "'></img>",
				}).appendTo(parentDiv);
			thumbnails.push(thumbnail);
			count += 1;
		}
		callback(thumbnails);
	});
}
function generateTranscripts(sbvFile, parentDiv, callback) {
	var transcripts = new Array();
	var count = 0;
	var height = 0;
	var padding = parseInt($(parentDiv).css('padding-top'),10);
	$.getJSON(sbvFile, function(sbv) {
		for (var key in sbv) {
			var line = sbv[key];
			var id = parentDiv + "-child-" + count;
			var transcript = {"id": id, "start": line.start, "end": line.end, "count": count};
			$("<div/>", { id: id.substring(1),
				class: "transcript-item",
				html: line.subtitle,
			}).appendTo(parentDiv).ready(function() {
				$(parentDiv).attr("scrollHeight")[count] = $(id).height();
				$(parentDiv).trigger("childReady");
			});
			transcripts.push(transcript);
			count += 1
		}
		$(parentDiv).attr("children", count);
		$(parentDiv).childReady(function() {
			if($(parentDiv).attr("children") > 0) {
				$(parentDiv).attr("children", $(parentDiv).attr("children") - 1);
			}
			else {
				//Completed all children div loading
				for (var t in transcripts) {
					var transcript = transcripts[t];
					t.height = $(t.id).height();
				}
				callback(transcripts);
			}
		});
	});
}

//Replace with more efficient height counting (caching onload callback?)
function scrollTo(scrollObj, Objs, count) {
	var height = 0
	for (var i = 0; i < Math.max(0, count-1); i++) {
		height += $(Objs[i].id).height() + 10;
	}
	$(scrollObj).scrollTop(height);
}

