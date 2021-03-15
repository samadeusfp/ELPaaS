try:
    import sys
    import sqlite3
    import os
    import subprocess
    import requests
    import time
    import urllib3
    import shutil
    from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
    import numpy as np
    from pm4py.objects.log.importer.xes import factory as xes_import_factory

    TRACE_START = "TRACE_START"
    TRACE_END = "TRACE_END"
    EVENT_DELIMETER = ">>>"

    def privatize_df(log, event_int_mapping, epsilon, output):
        #get true df frequencies
        print("Retrieving Directly Follows Frequencies   ", end = '')
        df_relations = get_df_frequencies(log, event_int_mapping)
        print("Done")
        #privatize df frequencies
        print("Privatizing Log   ", end = '')
        df_relations = apply_laplace_noise_df(df_relations, epsilon)
        print("Done")
        #write to disk
        print("Writing privatized Directly Follows Frequencies to disk   ", end = '')
        write_to_dfg(df_relations, event_int_mapping, output)
        print("Done")

    def create_event_int_mapping(log):
        event_name_list=[]
        for trace in log:
            for event in trace:
                event_name = event["concept:name"]
                if not str(event_name) in event_name_list:
                    event_name_list.append(event_name)
        event_int_mapping={}
        event_int_mapping[TRACE_START]=0
        current_int=1
        for event_name in event_name_list:
            event_int_mapping[event_name]=current_int
            current_int=current_int+1
        event_int_mapping[TRACE_END]=current_int
        return event_int_mapping

    def get_df_frequencies(log, event_int_mapping):
        print("print1")
        classifier = XEventNameClassifier()
        print("print2")
        df_relations = np.zeros((len(event_int_mapping),len(event_int_mapping)), dtype=int)
        print("print3")
        for trace in log[0]:
            current_event = TRACE_START
            print("print4")
            for event in trace:
                print("print4.5")
                print("event type:",type(event))
                next_event = classifier.get_class_identity(event)
                print("print5")
                current_event_int = event_int_mapping[current_event]
                next_event_int = event_int_mapping[next_event]
                df_relations[current_event_int, next_event_int] += 1
                print("print5")
                current_event = next_event

            current_event_int = event_int_mapping[current_event]
            print("print6")
            next_event = TRACE_END
            next_event_int = event_int_mapping[next_event]
            print("print7")
            df_relations[current_event_int, next_event_int] += 1
        return df_relations

    def apply_laplace_noise_df(df_relations, epsilon):
        lambd = 1/epsilon
        for cell in df_relations:
            a = cell[0]
            b = cell[1]
            noise = int(np.random.laplace(0, lambd))
            df_relations[a,b] = df_relations[a,b] + noise
            if df_relations[a,b]<0:
                df_relations[a,b]=0
        return df_relations

    def write_to_dfg(df_relations, event_int_mapping, output):
        out=output+".dfg"
        print("\n output_path: ",out,"\n")
        f = open(out,"w+")
        f.write(str(len(df_relations)-2)+"\n")
        for key in event_int_mapping:
            if not (str(key)==TRACE_START or str(key)==TRACE_END):
                f.write(str(key)+"\n")

        #starting activities
        no_starting_activities=0
        starting_frequencies=[]
        for x in range(1,len(df_relations)):
            current = df_relations[0,x]
            if current!=0:
                no_starting_activities+=1
                starting_frequencies.append((x-1,current))
        f.write(str(no_starting_activities)+"\n")
        for x in starting_frequencies:
            f.write(str(x[0])+"x"+str(x[1])+"\n")

        #ending activities
        no_ending_activities=0
        ending_frequencies=[]
        for x in range(0,len(df_relations)-1):
            current = df_relations[x,len(df_relations)-1]
            if current!=0:
                no_ending_activities+=1
                ending_frequencies.append((x-1, current))
        f.write(str(no_ending_activities)+"\n")
        for x in ending_frequencies:
            f.write((str(x[0])+"x"+str(x[1])+"\n"))

        #df relations
        for x in range(1,len(df_relations)-1):
            for y in range(1,len(df_relations)-1):
                if df_relations[x,y]!=0:
                    f.write(str(x-1)+">"+str(y-1)+"x"+str(df_relations[x,y])+"\n")
        f.close


    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]
    
    #preprocess file
    #os.mkdir(secure_token)
    print("\n Starting privatize_df.py \n")
    outPath = filePath.replace(".xes","_%s" % (epsilon))
    log = xes_import_factory.apply(filePath)
    event_mapping = create_event_int_mapping(log)
    privatize_df(log, event_mapping, epsilon, outPath)
    print("print2")
    #write to db
    print("Writing to DB")
    print(outPath)
    puffer,targetFile = outPath.split("media"+os.path.sep)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()

    #cleanup
    #shutil.rmtree(os.getcwd()+os.path.sep+secure_token)
except Exception as e:
    print("\n Error in privatize_df.py \n")
    f=open("debug","w+")
    f.write(str(e))
    if hasattr(e, 'message'):
        f.write(str(e.__class__.__name__) + ": " + e.message)
    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]
    f.write(filePath)
    f.write(epsilon)
    f.write(dbName)
    f.write(secure_token)
    f.close()
    #cleanup
    #shutil.rmtree(os.getcwd()+os.path.sep+secure_token)
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()

