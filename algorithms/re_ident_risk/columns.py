try:
    import smtplib
    import sys
    import pandas as pd
    import sqlite3
    import os
    import random
    import numpy as np
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.csv import factory as csv_exporter

    #set parameters

    filePath = sys.argv[1]
    dbName = sys.argv[2]
    secure_token = sys.argv[3]

    print("Retrieving case and event attribute names")
    filePath = filePath.replace(" ","_")
    
    log = xes_import_factory.apply(filePath)
    targetFilePath = filePath.replace(".xes","_renamed.csv")
    file_path_buffer = filePath.replace(".xes","_buffer.csv")
    csv_exporter.export(log, file_path_buffer)
    xes_csv_file = pd.read_csv(file_path_buffer, delimiter=",",skipinitialspace=True, encoding="utf-8-sig", keep_default_na=False, na_values=['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a', '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', ''])
    
    #####################################################

    if not 'Activity' in xes_csv_file.columns:
        print("Changing concept:name to Activity,case:concept:name to Case ID")
        xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
    if not 'Duration' in xes_csv_file.columns:
        xes_csv_file.loc[:,"Duration"] = 0.0

    #xes_csv_file = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig", keep_default_na=False, na_values=['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a', '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', ''])
    ###

    all_attributes = list(xes_csv_file.columns.values.tolist())
    all_attributes.remove('Activity')
    all_attributes.remove('Case ID')
    all_attributes.remove('time:timestamp')
    is_case_attribute_list = np.zeros(len(all_attributes), dtype=int)
    case_ids = pd.Series(xes_csv_file['Case ID'].unique())
    ###iterate thorugh log to find case attributes
    for case in case_ids:
        df = xes_csv_file.loc[xes_csv_file['Case ID'] == case]
        for attr in all_attributes:
            is_case_attribute_list[all_attributes.index(attr)] = is_case_attribute_list[all_attributes.index(attr)] + df[attr].count()
            
        del df
    
    number_of_cases = len(case_ids)
    case_attributes = []
    for i in range(len(is_case_attribute_list)): 
        if is_case_attribute_list[i] == number_of_cases:
            case_attributes.append(all_attributes[i])
    event_attributes = []
    new_list = []
    for attribute in all_attributes:
        if attribute not in case_attributes:
            event_attributes.append(attribute)
    
    print("\n All Attributes(excl Case ID, Activity): \n",all_attributes,"\n")
    print("\n Case Attributes: \n",case_attributes,"\n")
    print("\n Event  Attributes: \n",event_attributes,"\n")
    ###
    #column_list = list(xes_csv_file.columns.values.tolist()) 
    #column_list.remove('Activity')
    #column_list.remove('Case ID')
    #column_list.remove('time:timestamp')
    
    puffer,targetFile = targetFilePath.split("media"+os.path.sep)
    case_attributes_path = puffer +"media" +os.path.sep + secure_token +os.path.sep + "case_attributes.txt"
    event_attributes_path = puffer +"media" +os.path.sep + secure_token +os.path.sep + "event_attributes.txt"
    #targetFile = secure_token +os.path.sep + "columns.txt"
    #print(column_path)
    with open(case_attributes_path, 'w') as filehandle:
        filehandle.writelines("%s\n" % column for column in case_attributes)
        
    with open(event_attributes_path, 'w') as filehandle:
        filehandle.writelines("%s\n" % column for column in event_attributes)
        
    print("\n case and event attributes saved.\n")
    #write to db
    xes_csv_file.to_csv(targetFilePath, sep = ",")
    
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
    
