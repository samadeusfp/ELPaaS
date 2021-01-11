try:
    import smtplib
    import sys
    import pandas as pd
    import sqlite3
    import os
    import pretsa
    import random
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.importer.csv import factory as csv_import_factory
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    from pm4py.objects.log.exporter.csv import factory as csv_exporter
    

    #set parameters

    filePath = sys.argv[1]
    k = sys.argv[2]
    t = sys.argv[3]
    anon = sys.argv[4]
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    sys.setrecursionlimit(3000)
    
    filePath = filePath.replace(" ","_")
    if filePath.endswith(".xes"):
        log = xes_import_factory.apply(filePath)
        file_path_xes_csv = filePath + ".csv"
        csv_exporter.export(log, file_path_xes_csv)
    targetFilePath = file_path_xes_csv.replace(".xes.csv","_k%s_pretsa.csv" % (k))

    #run PRETSA
    if file_path_xes_csv.endswith(".xes.csv"):
        xes_csv_file = pd.read_csv(file_path_xes_csv, delimiter=",",skipinitialspace=True, encoding="utf-8-sig", keep_default_na=False, na_values=['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a', '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', ''])
        xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
        if not 'Duration' in xes_csv_file.columns:
            xes_csv_file.loc[:,"Duration"] = 0.0
        xes_csv_file.to_csv(file_path_xes_csv,sep=";",encoding="utf-8-sig",index=False)
    eventLog = pd.read_csv(file_path_xes_csv, delimiter=";",skipinitialspace=True, encoding="utf-8-sig", keep_default_na=False, na_values=['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a', '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', ''])
    pretsa_alg = pretsa.Pretsa(eventLog)
    print("PRETSA pre-processing done.")
    cutOutCases = pretsa_alg.runPretsa(int(k),float(t))
    privateEventLog = pretsa_alg.getPrivatisedEventLog()
    print("PRETSA algorithm done.")
    
    if anon:
        print("Anonymizing Case IDs...")
        caseIDs = pd.Series(privateEventLog['Case ID'].unique())
        caseList = caseIDs.tolist()
        intList = list(range(caseIDs.size))
        random.shuffle(intList)

        for i,row in privateEventLog.iterrows():
            privateEventLog.at[i,'Case ID'] = intList[caseList.index(row['Case ID'])]
            

    privateEventLog.to_csv(targetFilePath, sep=",",index=False)

    print("Writing to DB")
    puffer,targetFile = targetFilePath.split("media"+os.path.sep)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()


except:
    print("PRETSA algorithm has failed.")
    filePath = sys.argv[1]
    k = sys.argv[2]
    t = sys.argv[3]
    anon = sys.argv[4]
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
