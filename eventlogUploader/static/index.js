$(document).ready(function() {
	$("#id_algorithm").val("1");
	//assumes pretsa is initial algorithm
	$('#div_id_epsilon').css("display", "none");
	$('#div_id_k').css("display", "block");
	$('#div_id_t').css("display", "block");
	$('#div_id_anon').css("display", "block");
	$('#div_id_n').css("display", "none");
	$('#div_id_p').css("display", "none");
	//$('[data-toggle="popover"]').popover();
	

})

$('#id_algorithm').change(function(){
	var valueSelected = this.value;

	
		if (valueSelected == 1){
			//$(this).attr("data-content","Assumes a .csv File as Input. Returns a .csv File. The File needs to contain the columns 'Case ID', 'Activity' and 'Duration'").data("bs.popover");
			//$(this).popover("show")
			$('#div_id_epsilon').css("display", "none");
			$('#div_id_k').css("display", "block");
			$('#div_id_t').css("display", "block");
			$('#div_id_anon').css("display", "block");
			$('#div_id_n').css("display", "none");
			$('#div_id_p').css("display", "none");

		}
		else if (valueSelected ==2){
			//$(this).attr("data-content","Assumes a .xes File as Input. Returns a .dfg File.").data("bs.popover");
			//$().popover("show")
			$('#div_id_epsilon').css("display", "block");
			$('#div_id_k').css("display", "none");
			$('#div_id_t').css("display", "none");
			$('#div_id_anon').css("display", "none");
			$('#div_id_n').css("display", "none");
			$('#div_id_p').css("display", "none");
		}
		else if (valueSelected ==3){
			//$(this).attr("data-content","Assumes a .xes File as Input. Returns a .xes File.").data("bs.popover");
			//$('[data-toggle="popover"]').popover("show")
			$('#div_id_epsilon').css("display", "block");
			$('#div_id_k').css("display", "none");
			$('#div_id_t').css("display", "none");
			$('#div_id_anon').css("display", "none");
			$('#div_id_n').css("display", "block");
			$('#div_id_p').css("display", "block");
	}
})





function copyTokenToClipboard() {
  var $temp = $("#token").text();
  $temp = $temp.trim().split(":")[1].trim();
  //$("body").append($temp);
  var dummy = document.createElement("textarea");
  document.body.appendChild(dummy);
  dummy.value = $temp;
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);
}
