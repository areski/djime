$(document).ready(function () {
  $("#id_project").change(function() {
    if ($(this).parents("form").hasClass('billing')) {
      get = {'get': 'all'}
    }
    else {
      get = {'get': 'user'}
    }
    $.get('/time/json/project/' + $("#id_project").val(), get, function(data) {
      $("#id_task").html(data);
    });
  });
  $("tbody td.track span").click(function () {
    task_id = $(this).attr('class').match(/^\d+/)[0]
    djime.timer = $(this);
	  if ($(this).parents("td").hasClass('timer-added')) {
	    // Timer is active, must stop the time and update
	    $(this).parents("td").removeClass('timer-added').end()
	      .parents("tr").removeClass('timer-added').end()
	      .timeclock('destroy');
	    $("#task-timer-sidebar-button").timeclock('destroy');
	    $.post('/time/ajax/task/' + task_id + '/stop/');
	    $.getJSON('/time/ajax/task/' + task_id + '/get_json/', function(data) {
	      $("#djime-statusbar").find("p.total-time  > span").text(data.task_time).end()
	        .find("p.task > span").text(data.task_summary).end()
	        .find("p.project > span").text(data.project);
	    });
	  }
	  else {
	    // timer is inactive must stop the active and remove classes.
	    $("tbody tr.timer-added").removeClass('timer-added')
	      .find("td.timer-added").removeClass('timer-added')
	      .find("span").timeclock('destroy');
	    $(this).parents("td").addClass('timer-added').end()
	      .parents("tr").addClass('timer-added').end()
	      .timeclock();
	    $("#task-timer-sidebar-button").timeclock('destroy');
	    $.post('/time/ajax/task/' + task_id + '/start/');
	    $.getJSON('/time/ajax/task/' + task_id + '/get_json/', function(data) {
	      $("#djime-statusbar").find("p.total-time > span").text(data.task_time).end()
	        .find("p.task > span").text(data.task_summary).end()
	        .find("p.project > span").text(data.project);
	      djime.timer.parents('td').prev().text(data.task_time);
	    });
	    djimeStatusBar(task_id);
	  }
	});
	// Add active timeclock if task is in the table.
	if (djime.task_statusbar_id) {
	  djime.timer = $("tbody td.track span." + djime.task_statusbar_id).timeclock({since: djime.current_time})
	    .parents("td").addClass('timer-added').end()
	    .parents("tr").addClass('timer-added').end();
	}
	// Add statistics plot if data is available
	if (djime.flot_data) {
	  $.plot($("#flot"),
	  [{
	    data: djime.flot_data.flot,
	    color: "#99BBCC",
	    bars: {
	      show: true,
	      barWidth: 40000000,
	      align: "center"
	    },
	  }],
	  {
	    xaxis: {
	      mode: "time",
	      min: djime.flot_data.min * 0.99997,
	      max: djime.flot_data.max * 1.00003
	    },
	    yaxis: {
	      mode: "time",
	      min: 0
	    }
	  });
    $("input#stat-prev").click(function() {
      if (djime.flot_data.current_value > 1) {
        djime.flot_data.current_value -= 1;
      }
      updateGraph('current');
    });
    $("input#stat-next").click(function() {
      if ((djime.flot_data.meth == 'week' && djime.flot_data.current_value < 53) || (djime.flot_data.meth == 'month' && djime.flot_data.current_value < 12) || (djime.flot_data.meth == 'quarter' && djime.flot_data.current_value < 4) || (djime.flot_data.meth == 'year')) {
        djime.flot_data.current_value += 1;
        updateGraph('current');
      }
    });
    $("input#stat-orig").click(function() {
      updateGraph('original');
    });
	}
	$("div.outer").hide().filter("div." + $("#timesheet-select input:checked").val()).show();
  $("form#timesheet-select input").click(function () {
    $("div.outer").hide().filter("." + $(this).val()).show();
  });
	$("#id_begin, #id_end").datepicker({
	  firstDay: 1,
		dateFormat: 'yy-mm-dd',
		doneButtonText: 'Choose',
		changeMonth: true,
		changeYear: true,
	});
});

updateGraph = function (state) {
  if (state == 'current') {
    var value = djime.flot_data.current_value;
  }
  else {
    var value = djime.flot_data.meth_value;
  }
  $.getJSON(document.URL.substr(0, document.URL.search(/\/time\/statistics\//)) + '/time/statistics/ajax/flot/' + djime.flot_data.meth + '/' + value + '/',
    function(data) {
      $.plot($("#flot"),
  	  [{
  	    data: data.flot,
  	    color: "#99BBCC",
  	    bars: {
  	      show: true,
  	      barWidth: 40000000,
  	      align: "center"
  	    },
  	  }],
  	  {
  	    xaxis: {
  	      mode: "time",
  	      min: data.min * 0.99997,
  	      max: data.max * 1.00003
  	    },
  	    yaxis: { mode: "time" }
  	  });
  	  if (state == 'current') {
        $("#flot-headline").text('Now showing ' + djime.flot_data.meth + ' ' + value);
      }
      else {
       $("#flot-headline").text('');
      }
    });
}
