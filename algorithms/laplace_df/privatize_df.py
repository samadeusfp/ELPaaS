from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
import numpy as np

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
    print("Writing privatpized Directly Follows Frequencies to disk   ", end = '')
    write_to_dfg(df_relations, event_int_mapping, output)
    print("Done")

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
