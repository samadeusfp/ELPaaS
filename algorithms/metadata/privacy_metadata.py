try:
    import smtplib
    import sys
    import pandas as pd
    import sqlite3
    import os
    import random
    import time
    import numpy as np
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    from pm4py.objects.log.importer.csv import factory as csv_import_factory    
    from pm4py.objects.log.exporter.csv import factory as csv_exporter
    from p_privacy_metadata.privacyExtension import privacyExtension
    from p_privacy_metadata.ELA import ELA

    from pm4py.objects.conversion.log import converter as log_converter

         
    def convert_list_to_string(org_list, seperator=','):
    
        return seperator.join(org_list)
   
    #set parameters

    filePath = sys.argv[1]
    algorithm = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]
    waiting_message = 0
    while not os.path.exists(filePath):
        if waiting_message == 0:
            
            print("\n Privacy_metadata.py waiting for finished log ... \n")
            waiting_message = 1
        time.sleep(5)
    time.sleep(1)   
    print("\n Privacy_metadata.py found a finished log! \n")
    filePath = filePath.replace(" ","_")
    if algorithm== 'pretsa':
        xes_csv_file = pd.read_csv(filePath, delimiter=",",skipinitialspace=True, encoding="utf-8-sig", keep_default_na=False, na_values=['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a', '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', ''])
        targetFilePath = filePath.replace(".csv","_incl_metadata.xes")

    else:
        log = xes_import_factory.apply(filePath)
        targetFilePath = filePath.replace(".xes","_incl_metadata.xes")
        file_path_buffer = filePath.replace(".xes","_buffer.csv")
        csv_exporter.export(log, file_path_buffer)
        xes_csv_file = pd.read_csv(file_path_buffer, delimiter=",",skipinitialspace=True, encoding="utf-8-sig", keep_default_na=False, na_values=['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a', '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', ''])
        
    #####################################################

    if not 'Activity' in xes_csv_file.columns:
        print("Changing concept:name to Activity,case:concept:name to Case ID")
        xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
    if not 'Duration' in xes_csv_file.columns:
        xes_csv_file.loc[:,"Duration"] = 0.0

    all_attributes = list(xes_csv_file.columns.values.tolist())
    all_attributes.remove('Activity')
    all_attributes.remove('Case ID')
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
    event_attributes= []
    new_list = []
    for attribute in all_attributes:
        if attribute not in case_attributes:
            event_attributes.append(attribute)
    
    print("\n All Attributes(excl Case ID, Activity): \n",all_attributes,"\n")
    print("\n Case Attributes: \n",case_attributes,"\n")
    print("\n Event  Attributes: \n",event_attributes,"\n")
    
    if algorithm=='pretsa':
        xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
        xes_csv_file.rename(columns={'Case ID': 'case:concept:name', 'Activity': 'concept:name'}, inplace=True)
        #parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'case'}
        log = log_converter.apply(xes_csv_file)
        print("conersion applied")
    

    # privacyExtension Part
    prefix = 'privacy:'
    uri = 'paper_version_uri/privacy.xesext'
    privacy = privacyExtension(log, prefix, uri)

    if algorithm=='pretsa':
        print("Adding meta data to pretsa log")
        pretsa_event_attributes = event_attributes.copy()
        pretsa_event_attributes.remove('Duration')
        case_string= convert_list_to_string(case_attributes)
        event_string= convert_list_to_string(pretsa_event_attributes)
        
        #privacy.set_anonymizer(operation='suppression', level='event', target='org:resource')
        privacy.set_anonymizer(operation='substitution', level='event', target='concept:name')
        if 'Duration' in all_attributes:
            print("Duration found as column")
            privacy.set_anonymizer(operation='substitution', level='event', target='duration')
            privacy.set_anonymizer(operation='suppression', level='event', target='duration') 
            privacy.set_anonymizer(operation='suppression', level='trace', target='duration') 
            if event_string:
                privacy.set_anonymizer(operation='suppression', level='event', target=event_string)
            else:
                print("no additional event attributes to analyze for metadata found.")
            if case_string:
                privacy.set_anonymizer(operation='suppression', level='event', target=case_string)
            else:
                print("no additional case attributes to analyze for metadata found.")
    elif algorithm=='laplace_df':
        privacy.set_anonymizer(operation='substitution', level='event', target='concept:name')
    elif algorithm=='laplace_tv':
        privacy.set_anonymizer(operation='substitution', level='event', target='concept:name')
    elif algorithm=='pripel':
        privacy.set_anonymizer(operation='substitution', level='event', target='concept:name')
    else:
        print("unknown algorithm as argument in privacy_metadata.py")
    #pretsa: operation type "substitution", level "event", target "concept:name";
    #operation type "substitution", level "event", target "duration" (anders xes, zwei zeilen ausprobieren)
    #operation type "supression", level "event", target all other attributes
    #operation type "supression", level "trace", target all other attributes
 
    #falls anon: type "substitution", level "trace", target "concept:name"


    statistics={}
    statistics['no_modified_traces'] = 15
    statistics['no_modified_events'] = 20
    desired_analyses= {}
    desired_analyses['1']='process discovery'
    desired_analyses['2']='social network discovery'
    message = privacy.set_optional_anonymizer(layer = 1, statistics=statistics, desired_analyses=desired_analyses, test='test' )
    print(message)

    layer = privacy.get_anonymizer(layer=1)
    anon = privacy.get_anonymizations()
    xes_exporter.export_log(log, targetFilePath)
    print("metadata added.")
    # ELA Part
    #try:
    #    log_name = log.attributes['concept:name']
    #except Exception as e:
    #    log_name = "No mame is given for the event log!"
    
    
    ##do stuff
    #xes_exporter.export_log(log, targetFilePath)
    
    puffer,targetFile = targetFilePath.split("media"+os.path.sep)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()

except:
    filePath = sys.argv[1]
    algorithm = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]

    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    print("failed to add metadata.")
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
