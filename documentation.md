# Documentation

## How to add a new algorithm:

1.Create directory in ELPaaS\algorithms with python-script ( e.g. *new_algorithm.py*)

2.In *new_algorithm.py* make sure to include these arguments and lines(look at runPretsa.py for reference)
[try/except strucure is important so you know when a algorithm has failed or is just taking a while]
:

```
try:
    import sys

    filePath = sys.argv[1]  								### links to the uploaded file
    dbName = sys.argv[2]									### links to database where the output will be saved
    secure_token = sys.argv[3]								### key that identifies the file in the database
    
    ### open file at filePath
	
	#########################################	
	### this is where your algorithm goes ###
	#########################################
	
	targetFilePath = filePath.replace(".xes","newFileEnding.xes") ### create a new output file name
	
	### export file at targetFilePath
	
	
    puffer,targetFile = targetFilePath.split("media"+os.path.sep)	### database requires path that looks like  *securetoken here*\\targetFilename.xes 
    conn = sqlite3.connect(dbName)									
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))  ### saves file to database 
    conn.commit()
    conn.close()

except:
    filePath = sys.argv[1]
    dbName = sys.argv[2]
    secure_token = sys.argv[3]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
```

3. In *forms.py* add your algorithm to class DocumentForm
```
    algorithm = forms.ChoiceField(
        choices=(
                 ("1","PRETSA"),
                 ("2","Laplacian df-based"),
                 ("3","Laplacian tv-based"),
                 ("4","PRIPEL"),
                 ("5","Quantifying Re-identification Risk"),
				 ("6","New Algorithm"),
                ),
        #help_text ="Assumes a .csv File as Input. Returns a .csv File. The File needs to contain the columns 'Case ID', 'Activity' and 'Duration'"
    )
```
4. Add any new parameter your algorithm needs as a django field type in class DocumentForm

5. In *index.js* add any new parameters to the list, this is used to hide/unhide parameters based on the algorithm selected in the drop down menu:
	**$("#id_algorithm").val("1")** refers to the algorithm choice 1, so PRETSA
	Add a new block with your algorithm id e.g.:
	```
	else if (valueSelected ==6){}
	```
6. In *tasks.py* add a new @shared_task block that uses Popen to open your *new_algorithm.py*

7. If you choose to include the option of adding privacy metadata, make sure the the input to *privacy_metadata.py* matches the output path of your algorithm
Within *privacy_metadata.py* specify the anonymizer operation you wish to use
```
elif algorithm=='new_algorithm':
        privacy.set_anonymizer( ... )
```
8. in *views.py* include elif-options for your algorithm in *def handle_file_upload(request)*