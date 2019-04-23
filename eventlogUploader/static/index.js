
$('#view_file_form').on('submit', function(event){
	event.preventDefault();
	formData = $('#view_file_form');
	
	$.ajax({
			url: "view/",
			type: "POST",
			data: formData.serialize(),
			
			success: function(json){
				//toggle off the modal and show the files
				$('#view_file').modal('hide');

				if(json.length==0){
					$("#information_area").html("Sorry! We could not find any document");
				}
				else{
					alert(MEDIA_URL);
					var token = json[0].token;
					$("#information_area").html("Token: "+token);
					var doc_table = $("#file_table_body");
					for(var i=0; i<json.length;i++){
						var document=json[i].docfile;
						new_row='<tr><td>'+document+'</a></td><td>Finished</td><td>DATETIME</td></tr>'
						doc_table.append(new_row)
					}
				}
			}
	})
})
