$(document).ready(function () {
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