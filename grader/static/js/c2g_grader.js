/*
 * File:   c2g_exercises.js
 * Author: Chris Lewis (cmslewis@gmail.com)
 * =============================================================================
 * This file contains preliminary JS code for the Class2Go exercise pages,
 * all of which belong to the CS145 database course right now.
 */

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');



$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function csrfSafeMethod(method) {
}

$('.question .submit').click(function() {


  var $wrapper = $(this).closest('.question');

  var postData = {
    'grader_name':   'Octave_Grader',
    'select_dict':   '',
    'student_input': $wrapper.find('textarea').val(),
    'database-file': 'homeloan_test.m',
    'answer-file': 'homeloan_soln.m',
    'params': {
      'qnum':          $wrapper.data('qnum'),
      //'workbench-tag': 'SQL Movie-Rating Query Exercises (assigned)',
    }
  };
  
  $.post("/gradequery", postData, function(responseJSON) {

    //console.log(responseJSON);
    var responseData = $.parseJSON(responseJSON);
    //console.log(responseData);
    if ( responseData == "ERROR" ) {
      alert("Error: Invalid grader name");
      return;
    }


    //  $wrapper.find('.output').html( responseData.feedback[0].explanation );
      $wrapper.find('.output').html('Score: ' + responseData.score + ' ' + responseData.feedback.explanation);
  });


  
});

