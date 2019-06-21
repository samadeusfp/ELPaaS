try:
    import smtplib
    import sys
    import pandas as pd
    import sqlite3
    import os
    import pretsa
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.csv import factory as csv_exporter

    #set parameters

    filePath = sys.argv[1]
    k = sys.argv[2]
    t = sys.argv[3]
    dbName = sys.argv[4]
    secure_token = sys.argv[5]

    sys.setrecursionlimit(3000)
    filePath = filePath.replace(" ","_")
    if filePath.endswith(".xes"):
        log = xes_import_factory.apply(filePath)
        filePath = filePath + ".csv"
        csv_exporter.export(log, filePath)
    targetFilePath = filePath.replace(".csv","_t%s_k%s_pretsa.csv" % (t,k))
    #run PRETSA
    if filePath.endswith(".xes.csv"):
        xes_csv_file = pd.read_csv(filePath, delimiter=",",skipinitialspace=True, encoding="utf-8-sig")
        xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
        if not 'Duration' in xes_csv_file.columns:
            xes_csv_file.loc[:,"Duration"] = 0.0
        xes_csv_file.to_csv(filePath,sep=";",encoding="utf-8-sig",index=False)
    eventLog = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
    pretsa_alg = pretsa.Pretsa(eventLog)
    cutOutCases = pretsa_alg.runPretsa(int(k),float(t))
    privateEventLog = pretsa_alg.getPrivatisedEventLog()
    privateEventLog.to_csv(targetFilePath, sep=";",index=False)
    puffer,targetFile = filePath.split("media/")
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()

except:
    filePath = sys.argv[1]
    k = sys.argv[2]
    t = sys.argv[3]
    dbName = sys.argv[4]
    secure_token = sys.argv[5]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
