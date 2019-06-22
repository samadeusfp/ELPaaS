try:
    import sys
    import sqlite3
    import os
    import subprocess
    import requests
    import time

    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    n = sys.argv[3]
    p = sys.argv[4]
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    
    #preprocess file
    os.mkdir(secure_token)
    command = subprocess.Popen(["Rscript",
                                os.getcwd()+"/ProtectedLog/data/convert.R",
                                str(filePath),
                                str(secure_token)])
    command.communicate()
    if command.returncode != 1:
        raise Error

    #start pinq server
    server = subprocess.Popen([
        "mono",
        "ProtectedLog/bin/Release/ProtectedLog.exe",
        str(secure_token)+"/activities.csv",
        str(secure_token)+"/precedence.csv",
        str(secure_token)+"/log-sequences.csv",
        "100000"
        ])

    page = requests.get("http://localhost:1234/")
    timeout = 120
    while not page.status_code == 200:
        time.sleep(5)
        timeout -=5
        page = requests.get("http://localhost:1234/")
        if timeout<=0:
            server.kill()
            raise InputError

    outPath = filePath.replace(".xes","_%s_%s_%s.xes" % (epsilon, n, p))

    #get privatized log files
    command = subprocess.Popen(["Rscript",
                                os.getcwd()+"/ProtectedLog/data/discovery.R",
                                str(epsilon),
                                str(n),
                                str(p),
                                str(os.getcwd())+"/"+str(secure_token)+"/",
                                outPath]
                               ,cwd=os.getcwd()+"/ProtectedLog/data/")
    command.communicate()
    server.kill()
    if command.returncode != 1:
        raise InputError

    #write to db
    puffer,targetFile = outPath.split("media/")
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()
except:
    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    n = sys.argv[3]
    p = sys.argv[4]
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
