try:
    import smtplib
    import sys
    import pandas as pd
    import sqlite3
    import os
    import random
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    
    from p_privacy_metadata.privacyExtension import privacyExtension
    from p_privacy_metadata.ELA import ELA
    
    #set parameters

    filePath = sys.argv[1]
    dbName = sys.argv[2]
    secure_token = sys.argv[3]
    sys.setrecursionlimit(3000)
    
    filePath = filePath.replace(" ","_")
    log = xes_import_factory.apply(filePath)
    targetFilePath = filePath.replace(".xes","_incl_metadata.xes")
    ###

    # privacyExtension Part
    prefix = 'privacy:'
    uri = 'paper_version_uri/privacy.xesext'
    privacy = privacyExtension(log, prefix, uri)
    privacy.set_anonymizer(operation='suppression', level='event', target='org:resource')

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
    dbName = sys.argv[2]
    secure_token = sys.argv[3]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    print("failed to add metadata")
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
