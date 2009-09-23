updateTasks = function() {
  $.get('/time/json/project/' + $("#id_project").val(), function(data) {
    $("#id_task").html(data);
  });
}

$(document).ready(function () {
  $("#id_project").change(function() {
    updateTasks();
  });
  updateTasks();
});
