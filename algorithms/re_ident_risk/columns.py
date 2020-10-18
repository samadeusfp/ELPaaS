try:
    import smtplib
    import sys
    import pandas as pd
    import sqlite3
    import os
    import random
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.csv import factory as csv_exporter

    #set parameters

    filePath = sys.argv[1]
    dbName = sys.argv[2]
    secure_token = sys.argv[3]

    
    filePath = filePath.replace(" ","_")
    if filePath.endswith(".xes"):
        log = xes_import_factory.apply(filePath)
        filePath = filePath + ".csv"
        csv_exporter.export(log, filePath)
    targetFilePath = filePath.replace(".csv","_columns.csv")
    #run PRETSA
    if filePath.endswith(".xes.csv"):
        xes_csv_file = pd.read_csv(filePath, delimiter=",",skipinitialspace=True, encoding="utf-8-sig")
        xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
        if not 'Duration' in xes_csv_file.columns:
            xes_csv_file.loc[:,"Duration"] = 0.0
        xes_csv_file.to_csv(filePath,sep=";",encoding="utf-8-sig",index=False)
    
    eventLog = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
    
    column_list = list(eventLog.columns.values.tolist()) 
    column_list.remove('Activity')
    column_list.remove('Case ID')
    column_list.remove('time:timestamp')

    puffer,targetFile = targetFilePath.split("media"+os.path.sep)
    column_path = puffer +"media" +os.path.sep + secure_token +os.path.sep + "columns.txt"
    #targetFile = secure_token +os.path.sep + "columns.txt"
    #print(column_path)
    with open(column_path, 'w') as filehandle:
        filehandle.writelines("%s\n" % column for column in column_list)
        
    
    #write to db
    
    
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("Please continue with 'Select columns'", targetFile, secure_token))
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
    
