$(document).ready(function () {
	var both_timers = $('#task-timer-button, #task-timer-sidebar-button');

	// this button is getting data from the task view, so that start and stop
	// sends to the selected view.
	if (!($('#task-timer-button').hasClass('timer-added'))) {
		$('#task-timer-button.timer-running').timeclock({since: djime.current_time}).addClass('timer-added');
		$('#task-timer-button').addClass('timer-added').click(function () {
		  if ($(this).hasClass($.timeclock.markerClassName)) {
		    var elapsed = both_timers.timeclock('destroy');
		    $.post('/time/ajax/task/' + djime.task_page_id + '/stop/', {elapsed: elapsed});
		    $.getJSON('/time/ajax/task/' + djime.task_page_id + '/get_json/', function(data) {
		      $("#djime-statusbar p.total-time span").text(data.task_time);
		    });
		  }
		  else {
		    $.post('/time/ajax/task/' + djime.task_page_id + '/start/');
				$('#task-timer-sidebar-button').timeclock('destroy');
				$('#djime-statusbar .content').html('<p>Task: ' + djime.task_page_name + '</p><div id="task-timer-sidebar-button" class="timer-running"><div class="timeclock">0:00</div></div>');
		    both_timers = $('#task-timer-button, #task-timer-sidebar-button');
				$('#task-timer-sidebar-button').addClass('timer-added').click(function () {
				  if ($(this).hasClass($.timeclock.markerClassName)) {
				    var elapsed = both_timers.timeclock('destroy');
				    $.post('/time/ajax/task/' + djime.task_page_id + '/stop/', {elapsed: elapsed});
				    $.getJSON('/time/ajax/task/' + djime.task_page_id + '/get_json/', function(data) {
				      $("#djime-statusbar p.total-time span").text(data.task_time);
				    });
				  }
				  else {
				    $.post('/time/ajax/task/' + djime.task_page_id + '/start/');
				    both_timers.timeclock();
				  }
				});
				both_timers.timeclock();
		  }
		});
	}
	// This button is getting data from the timer object, so that it always sends
	// to the active task, and not the selected.
	if (!($('#task-timer-sidebar-button').hasClass('timer-added'))) {
		$('#task-timer-sidebar-button.timer-running').timeclock({since: djime.current_time}).addClass('timer-added');
		$('#task-timer-sidebar-button').addClass('timer-added').click(function () {
		  if ($(this).hasClass($.timeclock.markerClassName)) {
		    var elapsed = both_timers.timeclock('destroy');
		    $.post('/time/ajax/task/' + djime.task_statusbar_id + '/stop/', {elapsed: elapsed});
		    $.getJSON('/time/ajax/task/' + djime.task_statusbar_id + '/get_json/', {}, function(data) {
		      $("#djime-statusbar p.total-time span").text(data.task_time);
		    });
		  }
		  else {
		    $.post('/time/ajax/task/' + djime.task_statusbar_id + '/start/');
		    $('#task-timer-sidebar-button').timeclock();
				if($('#task-timer-button').hasClass(djime.task_statusbar_id)){
					$('#task-timer-button').timeclock();
				}
		  }
		});
	}
});