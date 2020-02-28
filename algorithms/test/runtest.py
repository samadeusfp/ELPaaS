import sys
import sqlite3
import os
import subprocess
import requests
import time
import urllib3
import shutil
import test
import smtplib
import pandas as pd


try:
    #set parameters

    filePath = sys.argv[1]
    dbName = sys.argv[2]
    secure_token = sys.argv[3]
    filePath = filePath.replace(" ","_")
    targetFilePath = filePath.replace(".csv","_test.csv" )

    eventLog = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
    eventLog.to_csv(targetFilePath, sep=";",index=False)

    puffer,targetFile = targetFilePath.split("media\\")
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()

    #print(eventLog)

except:
    filePath = sys.argv[1]
    dbName = sys.argv[2]
    secure_token = sys.argv[3]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()