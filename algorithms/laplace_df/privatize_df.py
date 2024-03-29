try:
    import sys
    import sqlite3
    import os
    import subprocess
    import requests
    import time
    import urllib3
    import shutil
    import glob

    from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
    from opyenxes.data_in.XUniversalParser import XUniversalParser
    #import opyenxes.factory.XFactory as xfactory
    import numpy as np
    from pm4py.objects.log import log as event_log
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log import util as log_utils
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    import random
    import datetime
    from dateutil.tz import tzutc
    TRACE_START = "TRACE_START"
    TRACE_END = "TRACE_END"
    EVENT_DELIMETER = ">>>"

    sys.setrecursionlimit(1000)

    def privatize_df(log, event_int_mapping, epsilon, output):
        #get true df frequencies
        print("Retrieving Directly Follows Frequencies   ", end = '')
        df_relations = get_df_frequencies(log, event_int_mapping)
        print("Done")
        #print(df_relations)
        #privatize df frequencies
        print("Privatizing Log   ", end = '')
        df_relations = apply_laplace_noise_df(df_relations, epsilon)
        print("Done")
        #write to disk
        print("Writing privatized Directly Follows Frequencies to disk   ", end = '')
        #write_to_dfg(df_relations, event_int_mapping, output)
        private_log = generate_pm4py_log(df_relations, event_int_mapping)
        xes_exporter.export_log(private_log,output)
        print("Done")

    def create_event_int_mapping(log):
        event_name_list=[]
        #print("\n log type:",type(log))
        for trace in log:
            #print("trace type:",type(trace))
            for event in trace:
                #print("event type:",type(event), event)
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
        #print("\n",type(event_int_mapping)," \n",event_int_mapping,"\n \n")
        return event_int_mapping

    def get_df_frequencies(log, event_int_mapping):
        classifier = XEventNameClassifier()
        df_relations = np.zeros((len(event_int_mapping),len(event_int_mapping)), dtype=int)
        for trace in log[0]:
            current_event = TRACE_START
            for event in trace:
                next_event = classifier.get_class_identity(event)
                current_event_int = event_int_mapping[current_event]
                next_event_int = event_int_mapping[next_event]
                df_relations[current_event_int, next_event_int] += 1
                current_event = next_event
            
            current_event_int = event_int_mapping[current_event]
            next_event = TRACE_END
            next_event_int = event_int_mapping[next_event]
            df_relations[current_event_int, next_event_int] += 1
            
        return df_relations

    def apply_laplace_noise_df(df_relations, epsilon):
        lambd = 1/float(epsilon)
        size = df_relations.shape[0]
        #print("\n",size,"\n")
        for i in range(size):
            for k in range(size):
                noise = int(np.random.laplace(0, lambd))
                df_relations[i,k] = df_relations[i,k] + noise
                if df_relations[i,k]<0:
                    df_relations[i,k]=0
        
        df_relations[:,0] = 0
        df_relations[0,size-1] = 0
        df_relations[size-1] = 0
        print(df_relations)
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

    def find_path(df_relations,possible_elements,existing_path,depth):
        
        current_activity = existing_path[-1]
        full_trace = False
        if current_activity == df_relations.shape[0]-1:
            #print("ends with:",current_activity,existing_path)
            full_trace = True
        if full_trace==False:
            if np.sum(df_relations[current_activity]) > 0:
                probabilities_current_df = df_relations[current_activity] / np.sum(df_relations[current_activity])
                next_activity = np.random.choice(possible_elements,p=probabilities_current_df)
                existing_path.append(next_activity)
                if df_relations[existing_path[-2],existing_path[-1]] > 0:
                    df_relations[existing_path[-2],existing_path[-1]] -= 1
                depth += 1
                if depth == 500:
                    print(existing_path)
                    print(df_relations)
                    return [0]
                existing_path=find_path(df_relations,possible_elements,existing_path,depth)
            else:
                
                #print(existing_path,"backtracking to ", existing_path[:-1],"dead end at:",existing_path[-1])
                
                if current_activity == 0:
                    print("No more viable paths to TRACE_END")
                    return [0]
                depth += 1
                    
                df_relations[existing_path[-2],existing_path[-1]] += 1 
                df_relations[:,existing_path[-1]] = 0            
                existing_path = existing_path[:-1]
                existing_path = find_path(df_relations,possible_elements,existing_path,depth) 
                
                
        return existing_path
     
    def generate_pm4py_log(df_relations, event_int_mapping):
        int_event_mapping = {value:key for key, value in event_int_mapping.items()}
        log = event_log.EventLog()
        size = df_relations.shape[0]-1
        #print(np.sum(df_relations[0]),np.sum(df_relations,axis=0)[size])
        trace_amount = min(np.sum(df_relations[0]),np.sum(df_relations,axis=0)[size])
        possible_elements = list(range(0,size+1))
        counter = 0
        while(counter < trace_amount):
            empty_list=[0]
            next_trace = find_path(df_relations,possible_elements ,empty_list,0)
            #print("trace nr.: ",counter,next_trace)
            if len(next_trace) <= 1:
                print("All traces attached to log.")
                break
            
            trace = event_log.Trace()
            trace.attributes["concept:name"] = counter
            counter += 1
            
            
            for i in range(len(next_trace)-1):
                #print(df_relations[next_trace[i],next_trace[i+1]])
                #if df_relations[next_trace[i],next_trace[i+1]] > 0:
                #    df_relations[next_trace[i],next_trace[i+1]] -= 1
                if str(int_event_mapping[next_trace[i]]) == TRACE_START:
                    continue
                event = event_log.Event()
                event["concept:name"] = str(int_event_mapping[next_trace[i]])
                event["time:timestamp"] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=tzutc())
                trace.append(event)
            
            log.append(trace)
            
        
        return log

    filePath = sys.argv[1]
    epsilon = sys.argv[2]
    dbName = sys.argv[3]
    secure_token = sys.argv[4]
    
    #preprocess file
    #os.mkdir(secure_token)
    print("\n Starting privatize_df.py \n")
    outPath = filePath.replace(".xes","_%s.xes" % (epsilon))
    log = xes_import_factory.apply(filePath)


    parser = XUniversalParser()

    if parser.can_parse(filePath):
        print("log can be parsed.")
    else:
        print("log can not be parsed.")

    log_file = open(filePath)
    log_list = parser.parse(log_file)
    #log = log_list[0]

    event_mapping = create_event_int_mapping(log)
    privatize_df(log_list, event_mapping, epsilon, outPath)

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

