import sys
import sqlite3
import os
import subprocess
import requests
import time

f=open("debug","w+")
f.write("Executing runLaplacian with params\n")
filePath = sys.argv[1]
epsilon = sys.argv[2]
dbName = sys.argv[3]
secure_token = sys.argv[4]
f.write("CWD      :"+str(os.getcwd()+"\n"))
f.write("FilePath :"+str(filePath)+"\n")
f.write("Epsilon  :"+str(epsilon)+"\n")
f.write("dbName   :"+str(dbName)+"\n")
f.write("Token    :"+str(secure_token)+"\n")

#preprocess file
os.mkdir(secure_token)
command = subprocess.Popen(["rscript",
                            os.getcwd()+"/ProtectedLog/data/convert.R",
                            str(filePath),
                            str(secure_token)])
command.communicate()
f.write("CSV Files generated at "+str(os.getcwd)+"/"+str(secure_token)+"\n")


#start pinq server
server = subprocess.Popen([
    "ProtectedLog/bin/Release/ProtectedLog.exe",
    str(secure_token)+"/activities.csv",
    str(secure_token)+"/precedence.csv",
    str(secure_token)+"/log-sequences.csv",
    "100000"
    ])
page = requests.get("http://localhost:1234/")
timeout = 120
f.write(str(page.status_code)+"\n")
while not page.status_code == 200:
    time.sleep(5)
    timeout -=5
    page = requests.get("http://localhost:1234/")
    f.write("Retrying connection: "+str(page.status_code)+"\n")
    if timeout<=0:
        f.write("Timeout while starting Server. Aborting process!")
        f.close()
        server.kill()
        sys.exit()
f.write("Server started")

outPath = filePath.replace(".xes","_%s.xes" % (epsilon))

#get privatized log files
command = subprocess.Popen(["rscript",
                            os.getcwd()+"/ProtectedLog/data/discovery.R",
                            str(epsilon),
                            outPath]
                           ,cwd=os.getcwd()+"/ProtectedLog/data/")
command.communicate()
server.kill()
#write to db
puffer,targetFile = outPath.split("media/")
conn = sqlite3.connect(dbName)
c = conn.cursor()
c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
conn.commit()
conn.close()
f.write("Done")
f.close()
