
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
					var token = json[0].token;
					$("#information_area").html("Token: "+token);
					var doc_table = $("#file_table_body");
					for(var i=0; i<json.length;i++){
						var document=json[i].docfile;
						var status=json[i].status;
						//<a href="{% static 'document.docfile.name' %}">{{ document.docfile.name }}</a>
						new_row='<tr><td><a href="'+media_adress+'/documents/'+document+'">'+document+'</a></td><td>'+status+'</td><td>DATETIME</td></tr>'
						doc_table.append(new_row)
					}
				}
			}
	})
})
