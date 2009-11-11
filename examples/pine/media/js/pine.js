$(document).ready(function() {
  /**
   * Function to handle clases on td elements to keep even/odd styling
   */
  djime.tablesort = function() {
    $("table.djime.task_list tr").each(function(index) {
      if (index % 2 == 0) {
        $(this).removeClass('odd').removeClass('even').addClass('even');
      }
      else {
        $(this).removeClass('odd').removeClass('even').addClass('odd');
      }
    });
  }
  $("table.djime.task_list").addClass("tablesorter").tablesorter();
  $("table.djime.task_list th").click(function() {
    setTimeout('djime.tablesort()', 100)
  });
});
