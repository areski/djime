updateTasks = function() {
  $.get('/time/json/project/' + $("#id_project").val(), function(data) {
    $("#id_task").html(data);
  });
}

$(document).ready(function () {
  $("#id_project").change(function() {
    updateTasks();
  });
  if ($("#id_project").val()){
    updateTasks();
  }
  $("tbody td.track span").click(function () {
	  if ($(this).parents("td").hasClass('timer-added')) {
	    // Timer is active, must stop the time and update
	    $(this).parents("td").removeClass('timer-added').end()
	      .timeclock('destroy');
	    $("#task-timer-sidebar-button").timeclock('destroy');
	    $.post('/time/ajax/task/' + $(this).attr('class').match(/^\d+/)[0] + '/stop/');
	    $.getJSON('/time/ajax/task/' + $(this).attr('class').match(/^\d+/)[0] + '/get_json/', function(data) {
	      $("#djime-statusbar").find("p.total-time span").text(data.task_time);
	    });
	  }
	  else {
	    // timer is inactive must stop the active and remove classes.
	    $("tbody td.timer-added").removeClass('timer-added').find("span").timeclock('destroy');
	    $(this).parents("td").addClass('timer-added').end()
	      .timeclock();
	    $("#task-timer-sidebar-button").timeclock('destroy').timeclock();
	    $.post('/time/ajax/task/' + $(this).attr('class').match(/^\d+/)[0] + '/start/');
	    $.getJSON('/time/ajax/task/' + $(this).attr('class').match(/^\d+/)[0] + '/get_json/', function(data) {
	      $("#djime-statusbar").find("p.total-time span").text(data.task_time).end()
	        .find("p.task span").text(data.task_summary).end()
	        .find("p.project span").text(data.project);
	    });
	  }
	});
	// Add active timeclock if task is in the table.
	if (djime.task_statusbar_id) {
	  $("tbody td.track span." + djime.task_statusbar_id).timeclock({since: djime.current_time})
	    .parents("td").addClass('timer-added');
	}
});

