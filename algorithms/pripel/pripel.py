try:
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    from pm4py.objects.log.util import sampling
    import tracematcher
    from attributeAnonymizier import AttributeAnonymizier as AttributeAnonymizier
    from trace_variant_query import privatize_tracevariants
    import datetime
    import sys
    import pandas as pd
    import sqlite3
    import os
    

    def freq(lst):
        d = {}
        for i in lst:
            if d.get(i):
                d[i] += 1
            else:
                d[i] = 1
        return d

    log_path = sys.argv[1]
    epsilon = float(sys.argv[2])
    N = int(sys.argv[3])
    k = int(sys.argv[4])

    dbName = sys.argv[5]###
    secure_token = sys.argv[6]###
    ################################## pripel code

    new_ending = "_epsilon_" + "_k" + str(k) + "_anonymizied.xes"
    result_log_path = log_path.replace(".xes",new_ending)
    print("\n output_path pripel: ",result_log_path,"\n")
    starttime = datetime.datetime.now()
    log = xes_import_factory.apply(log_path)

    starttime_tv_query = datetime.datetime.now()
    tv_query_log = privatize_tracevariants(log, epsilon, k, N)
    print(len(tv_query_log))
    endtime_tv_query = datetime.datetime.now()
    print("Time of TV Query: " + str((endtime_tv_query - starttime_tv_query)))
    print("print0")
    starttime_trace_matcher = datetime.datetime.now()
    print("print1")
    traceMatcher = tracematcher.TraceMatcher(tv_query_log,log)
    print("print2")
    matchedLog = traceMatcher.matchQueryToLog()
    print(len(matchedLog))
    endtime_trace_matcher = datetime.datetime.now()
    print("Time of TraceMatcher: " + str((endtime_trace_matcher - starttime_trace_matcher)))
    distributionOfAttributes = traceMatcher.getAttributeDistribution()
    occurredTimestamps, occurredTimestampDifferences = traceMatcher.getTimeStampData()
    print(min(occurredTimestamps))
    starttime_attribute_anonymizer = datetime.datetime.now()
    attributeAnonymizier = AttributeAnonymizier()
    anonymiziedLog, attritbuteDistribution = attributeAnonymizier.anonymize(matchedLog,distributionOfAttributes,epsilon,occurredTimestampDifferences,occurredTimestamps)
    endtime_attribute_anonymizer = datetime.datetime.now()
    print("Time of attribute anonymizer: " +str(endtime_attribute_anonymizer - starttime_attribute_anonymizer))
    print(result_log_path)
    result_log_path = result_log_path.replace("\\",os.path.sep)#####
    
    xes_exporter.export_log(anonymiziedLog, result_log_path)
    endtime = datetime.datetime.now()
    print("Complete Time: " + str((endtime-starttime)))

    print("Time of TV Query: " + str((endtime_tv_query - starttime_tv_query)))
    print("Time of TraceMatcher: " + str((endtime_trace_matcher - starttime_trace_matcher)))
    print("Time of attribute anonymizer: " +str(endtime_attribute_anonymizer - starttime_attribute_anonymizer))

    print(result_log_path)
    print(freq(attritbuteDistribution))
    
    ######################################
    
    puffer,targetFile = result_log_path.split("media"+os.path.sep)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()
    print("Done!")

except:
    log_path = sys.argv[1]
    epsilon = float(sys.argv[2])
    N = int(sys.argv[3])
    k = int(sys.argv[4])
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()