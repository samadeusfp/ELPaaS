import sys
import sqlite3
import os
import subprocess

f=open("debug","w+")
f.write("Executing runLaplacian with params\n")
filePath = sys.argv[1]
epsilon = sys.argv[2]
n = sys.argv[3]
p = sys.argv[4]
dbName = sys.argv[5]
secure_token = sys.argv[6]
f.write("CWD      :"+str(os.getcwd()+"\n"))
f.write("FilePath :"+str(filePath)+"\n")
f.write("Epsilon  :"+str(epsilon)+"\n")
f.write("n        :"+str(n)+"\n")
f.write("p        :"+str(p)+"\n")
f.write("dbName   :"+str(dbName)+"\n")
f.write("Token    :"+str(secure_token)+"\n")

#preprocess file
os.mkdir(secure_token)
f.write(str(os.getcwd())+"/ProtectedLog/data/convert.R")
command = subprocess.Popen(["rscript", os.getcwd()+"/ProtectedLog/data/convert.R", str(filePath), str(secure_token)])
command.communicate()
f.write("Done")
f.close()
