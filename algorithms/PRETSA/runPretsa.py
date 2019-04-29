import sys
import pandas as pd
import sqlite3

#set parameters
filePath = sys.argv[1]
k = sys.argv[2]
t = sys.argv[3]
dbName = sys.argv[4]
secure_token = sys.argv[5]
sys.setrecursionlimit(3000)
targetFilePath = filePath.replace(".csv","_t%s_k%s_pretsa.csv" % (t,k))

#run PRETSA
#eventLog = pd.read_csv(filePath, delimiter=";")
#pretsa = Pretsa(eventLog)
#cutOutCases = pretsa.runPretsa(int(k),float(t))
#privateEventLog = pretsa.getPrivatisedEventLog()
#privateEventLog.to_csv(targetFilePath, sep=";",index=False)

#save to file, change name to new

#Change existing entry instead of writing a new one, maybe add start and end time
#Add PRETSA result to django-model/sqlite
puffer,targetFile = targetFilePath.split("media/documents/")
conn = sqlite3.connect(dbName)
c = conn.cursor()
c.execute("INSERT INTO eventlogUploader_document(docfile, token, status) VALUES (?,?,?)",(targetFile,secure_token,"FINISHED"))
conn.commit()
conn.close()
