try:
    import sys
    import sqlite3
    import os
    import subprocess
    import requests
    import time
    import urllib3

    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]

    #preprocess file
    os.mkdir(secure_token)
    command = subprocess.Popen(["Rscript",
                                os.getcwd()+"/convert.R",
                                str(filePath),
                                str(secure_token)])
    command.communicate()
    if command.returncode != 0:
        raise Exception("Cannot convert data")

    #start pinq server
    server = subprocess.Popen([
        "mono",
        "bin/PDDP.exe",
        str(secure_token)+"/activities.csv",
        str(secure_token)+"/precedence.csv",
        str(secure_token)+"/log-sequences.csv",
        "100000"
        ])

    print("Trying to reach PINQ server")
    timeout = 120
    isReachable = False
    while not isReachable:
        if timeout<=0:
            server.kill()
            raise Exception("Cannot find PINQ")        
        try: 
            page = requests.get("http://localhost:1234/") #TODO choose random port
            isReachable = page.status_code == 200
        except requests.exceptions.RequestException as e:
            print("Waiting for PINQ ...")            
        timeout -=5        
        time.sleep(5)        

    print("Found PINQ server")
    outPath = filePath.replace(".xes","_%s.dfg" % (epsilon))

    print("Running `discovery.R`")
    #get privatized log files
    command = subprocess.Popen(["Rscript",
                                os.getcwd()+"/discovery.R",
                                str(epsilon),
                                outPath]
                               ,cwd=os.getcwd())
    command.communicate()
    server.kill()
    if command.returncode != 0:
        raise Exception("Cannot communicate to PINQ")

    #write to db
    puffer,targetFile = outPath.split("media/")
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()
except Exception as e:
    f=open("debug","w+")
    f.write(str(e))
    if hasattr(e, 'message'):
        f.write(str(e.__class__.__name__) + ": " + e.message)
    f.close()
    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()

