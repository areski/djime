$(document).ready(function () {
  djimeStatusBar();
});

djimeStatusBar = function(task_id) {
  if (!task_id) {
    task_id = djime.task_statusbar_id
  }
  else {
    var noop = true;
  }
  if (task_id) {
    $("#djime-statusbar").find(".message").hide().end().find(".timetracker").show();
    timer = $('#task-timer-sidebar-button');
  	if (!(timer.hasClass('timer-added'))) {
  	  if (noop) {
  	    timer.timeclock().addClass('timer-added');
  	  }
  	  else {
  		  $('#task-timer-sidebar-button.timer-running').timeclock({since: djime.current_time}).addClass('timer-added');
  		}
  		timer.addClass('timer-added').click(function () {
  		  if ($(this).hasClass($.timeclock.markerClassName)) {
  		    var elapsed = timer.timeclock('destroy');
  		    $.post('/time/ajax/task/' + task_id + '/stop/', {elapsed: elapsed});
  		    $.getJSON('/time/ajax/task/' + task_id + '/get_json/', {}, function(data) {
  		      $("#djime-statusbar p.total-time span").text(data.task_time);
  		    });
  		    $("td.track.timer-added").removeClass("timer-added")
  		      .parents("tr").removeClass("timer-added").end()
  		      .find("span").timeclock('destroy');
  		  }
  		  else {
  		    $.post('/time/ajax/task/' + task_id + '/start/');
  		    timer.timeclock();
  		    djime.timer.parents("td").addClass('timer-added').end()
    	    .parents("tr").addClass('timer-added').end()
    	    .timeclock();
  			}
  		});
  	}
  }
  else {
    $("#djime-statusbar .timetracker").hide();
  }
}