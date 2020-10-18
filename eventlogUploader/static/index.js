$(document).ready(function() {
	$("#id_algorithm").val("1");
	//assumes pretsa is initial algorithm
	$('#div_id_epsilon').css("display", "none");
	$('#div_id_k').css("display", "block");
	$('#div_id_t').css("display", "block");
	$('#div_id_anon').css("display", "block");
	$('#div_id_n').css("display", "none");
	$('#div_id_p').css("display", "none");
	$('#div_id_unique_identifier').css("display", "none");
	$('#div_id_attributes').css("display", "none");
	$('#div_id_attributes_to_exclude').css("display", "none");
	$("#id_projection").val("1");
	$('#div_id_case_attr').css("display", "none");
	$('#div_id_event_attr').css("display", "none");
	$('#div_id_token').css("display", "none");
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
			$('#div_id_unique_identifier').css("display", "none");
			$('#div_id_attributes').css("display", "none");
			$('#div_id_attributes_to_exclude').css("display", "none");
			

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
			$('#div_id_unique_identifier').css("display", "none");
			$('#div_id_attributes').css("display", "none");
			$('#div_id_attributes_to_exclude').css("display", "none");
			
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
			$('#div_id_unique_identifier').css("display", "none");
			$('#div_id_attributes').css("display", "none");
			$('#div_id_attributes_to_exclude').css("display", "none");
			
	    }
		else if (valueSelected ==4){
			//$(this).attr("data-content","Assumes a .xes File as Input. Returns a .xes File.").data("bs.popover");
			//$('[data-toggle="popover"]').popover("show")
			$('#div_id_epsilon').css("display", "none");
			$('#div_id_k').css("display", "none");
			$('#div_id_t').css("display", "none");
			$('#div_id_anon').css("display", "none");
			$('#div_id_n').css("display", "none");
			$('#div_id_p').css("display", "none");
			$('#div_id_unique_identifier').css("display", "none");
			$('#div_id_attributes').css("display", "none");
			$('#div_id_attributes_to_exclude').css("display", "none");
			
			
			//Check File API Support
			if (window.File && window.FileReader && window.FileList && window.Blob) {
				document.getElementById('id_docfile').onchange = document.getElementById('id_docfile').addEventListener('change', handleFileSelect, false);
				
				function handleFileSelect(event){
				  const reader = new FileReader()
				  reader.onload = handleFileLoad;
				  reader.readAsText(event.target.files[0])
				}

				function handleFileLoad(event){
				  console.log(event);
				  document.getElementById('id_test_return').textContent = event.target.result;
				}
				
			}
			else {
				alert('File API not supported in this browser. Consider using a more modern browser.');
			}
				
	    }			
})

$('#id_projection').change(function(){
	var valueSelected = this.value;

	
		if (valueSelected == 1 || valueSelected == 5){
			//$(this).attr("data-content","Assumes a .csv File as Input. Returns a .csv File. The File needs to contain the columns 'Case ID', 'Activity' and 'Duration'").data("bs.popover");
			//$(this).popover("show")
			
			$('#div_id_case_attr').css("display", "none");
			$('#div_id_event_attr').css("display", "none");
			$('#div_id_token').css("display", "none");
			
			

		}
		else if (valueSelected ==2){
			//$(this).attr("data-content","Assumes a .xes File as Input. Returns a .dfg File.").data("bs.popover");
			//$().popover("show")
			
			$('#div_id_case_attr').css("display", "block");
			$('#div_id_event_attr').css("display", "block");
			$('#div_id_token').css("display", "none");
			
			
		}
		else if (valueSelected ==3){
			//$(this).attr("data-content","Assumes a .xes File as Input. Returns a .xes File.").data("bs.popover");
			//$('[data-toggle="popover"]').popover("show")
			
			$('#div_id_case_attr').css("display", "none");
			$('#div_id_event_attr').css("display", "block");
			$('#div_id_token').css("display", "none");
			
			
	    }
		else if (valueSelected ==4){
			//$(this).attr("data-content","Assumes a .xes File as Input. Returns a .xes File.").data("bs.popover");
			//$('[data-toggle="popover"]').popover("show")
			
			$('#div_id_case_attr').css("display", "block");
			$('#div_id_event_attr').css("display", "none");
			$('#div_id_token').css("display", "none");
			
			
		
				
	    }			
})

/*

function doSomethingWithData(data) {
    alert(data);
}

$.get('rpc.php?o=' + id, doSomethingWithData);


*/
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

