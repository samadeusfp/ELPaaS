import sys
import pandas as pd
import sqlite3
import os
import pretsa
#change cwd to dir of script

#set parameters
filePath = sys.argv[1]
k = sys.argv[2]
t = sys.argv[3]
dbName = sys.argv[4]
secure_token = sys.argv[5]
sys.setrecursionlimit(3000)
targetFilePath = filePath.replace(".csv","_t%s_k%s_pretsa.csv" % (t,k))

#run PRETSA
eventLog = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
pretsa_alg = pretsa.Pretsa(eventLog)
cutOutCases = pretsa_alg.runPretsa(int(k),float(t))
privateEventLog = pretsa_alg.getPrivatisedEventLog()
privateEventLog.to_csv(targetFilePath, sep=";",index=False)

#save to file, change name to new

#Change existing entry instead of writing a new one, maybe add start and end time
#Add PRETSA result to django-model/sqlite
puffer,targetFile = targetFilePath.split("media/")
conn = sqlite3.connect(dbName)
c = conn.cursor()
c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("FINISHED", secure_token))

#print mail to user stating file is ready now?

#c.execute("INSERT INTO eventlogUploader_document(docfile, token, status) VALUES (?,?,?)",(targetFile,secure_token,"FINISHED"))
conn.commit()
conn.close()
