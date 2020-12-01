try:
    import smtplib
    import sys
    import pandas as pd
    import numpy as np
    import sqlite3
    import os
    import random
    from datetime import datetime
    from pm4py.objects.log.importer.xes import factory as xes_import_factory
    from pm4py.objects.log.exporter.csv import factory as csv_exporter
    from scipy.stats import itemfreq
    
    def generate_projection_view(projections_local, case_attribute_local, activity_local, event_attribute_local,
                             timestamp_local):
        """ Depending on the projection, the corresponding columns are selected."""

        if projections_local == "1":
            qi = []
            events = activity_local + timestamp_local
        elif projections_local == "2":
            qi = case_attribute_local
            events = activity_local + event_attribute_local
        elif projections_local == "3":
            qi = []
            events = activity_local + event_attribute_local
        elif projections_local == "4":
            qi = case_attribute_local
            events = activity_local
        elif projections_local == "5":
            qi = []
            events = activity_local
        else:
            sys.exit("The given projection '" + projections_local + "' is not a valid projection")
        return qi, events


    def prepare_data(events, data, attributes_local):
        """ Put the data in the right format. The column of the activities and event
        attributes consist of a list with the corresponding events.
        """
        for event in events:
            filter_col = [col for col in data if col.startswith(event)]
            col_name = event + '_combined'
            attributes_local.append(col_name)
            if type(data[filter_col[0]][0]).__name__ == 'str':
                data[col_name] = data[filter_col].apply(lambda row: row.tolist(), axis=1) 
                data[col_name] = data[col_name].apply(helps) 
            else:
                data[filter_col] = data[filter_col].astype(str)
                data[col_name] = data[filter_col].apply(lambda row: row.tolist(), axis=1)
                data[col_name] = data[col_name].apply(helps) 
        return data[attributes_local]


    def calculate_unicity(data, qi, events, number_points):
        """ Calculate the unicity based on randomly selected points.
        events[0] represents the column of activities. 
        The other events[1] ... events[len(events)-1] correspond to the other event attributes or timestamps.
        
        1. Activities and their correspondig attributes are selected randomly. We call them points. 
        2. Each case, more precisely all its points, are compared with the others.
        If the case is the only one with these points, it is declared as unique.
        The sum(uniques) represents the number of cases that are unique with the given points.
        3. Unicity is then the proportion of unique cases compared to the total number of cases.  
        """
        
        if number_points > 1:
            data = generate_random_points_absolute(data, events[0], number_points)
        else:
            data = generate_random_points(data, events[0], number_points)

        for k in range(1, len(events)):
            event = events[k]
            col_name = event + '_combined'
            col_name_new = event + '_points'
            data[col_name_new] = data.apply(make_otherpoints, args=[col_name, events[0]], axis=1)

        uniques = data.apply(uniqueness, args=[qi, events, data], axis=1)
        unicity = sum(uniques)/len(data)  
        return unicity


    def generate_random_points(data, activity_local, number_points_local):
        """ generates random points depending on the relative frequency """
        data['random_p'] = data.apply(lambda x:
                                      random.sample(list(enumerate(x[activity_local+'_combined'])),
                                                    int(len(x[activity_local + '_combined'])*number_points_local))
                                      if (int(len(x[activity_local+'_combined'])*number_points_local) > 1)
                                      else random.sample(list(enumerate(x[activity_local+'_combined'])), 1), axis=1)
        data['random_points_number'] = data.apply(lambda x: len(x.random_p), axis=1)
        data[activity_local + '_points'] = data.apply(makepoints, axis=1)
        data[activity_local + 'random_index'] = data.apply(getindex, axis=1)
        return data


    def generate_random_points_absolute(data, activity_local, number_points_local):
        """ generates random points depending max trace length """
        data['random_p'] = data.apply(lambda x:
                                      random.sample(list(enumerate(x[activity_local + '_combined'])),
                                                    number_points_local)
                                      if (len(x[activity + '_combined']) > number_points_local)
                                      else random.sample(list(enumerate(x[activity_local+'_combined'])),
                                                         len(x[activity_local+'_combined'])), axis=1)
        data['random_points_number'] = data.apply(lambda x: len(x.random_p), axis=1)
        data[activity_local + '_points'] = data.apply(makepoints, axis=1)
        data[activity_local + 'random_index'] = data.apply(getindex, axis=1)
        return data


    def check_subset(data, subset):
        """frequency of each element than compare them"""   
        if all(elem in data for elem in subset):
            data_freq = itemfreq(data)
            subset_freq = itemfreq(subset)
            for elem in subset_freq: 
                if elem[0] in data_freq[:, 0]:
                    itemindex = np.where(data_freq[:, 0] == elem[0])
                    if (len(elem[0]) != len(data_freq[itemindex][0][0])) or \
                            (int(data_freq[itemindex][0][1]) < int(elem[1])):
                        return False
                else:
                    return False
            return True
        return False


    def makepoints(x):
        values = []
        for idx, val in x['random_p']:
            values.append(val)
        return values


    def getindex(x):
        indexes = []
        for idx, val in x['random_p']:
            indexes.append(idx)
        return indexes


    def make_otherpoints(x, event,act):
        points = []
        indexes = x[act+'random_index']
        for i in indexes:
            if i < len(x[event]):
                points.append(x[event][i])
        return points


    def helps(x):
        n = len(x)-pd.Series(x).last_valid_index()
        del x[-n:]
        return x


    def equality(x, qi, events_to_concat, row):
        """return true if all conditions true"""
        if len(qi) > 0:
            for q in qi:
                if x[q] != row[q]:
                    return 0
        for e in events_to_concat:
            event_row = e + '_combined'
            points_row = e + '_points'
            if not check_subset(x[event_row], row[points_row]):
                return 0
        return 1


    def uniqueness(x, qi, events_to_concat, df_data):
        
        unique = df_data.apply(equality, args=[qi, events_to_concat, x], axis=1)
        if sum(unique) == 1:
            return 1
        return 0


    #set parameters
    
    filePath = sys.argv[1]
    projection = sys.argv[2]
    case_attribute_string = sys.argv[3]
    event_attribute_string = sys.argv[4]
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    sys.setrecursionlimit(3000)
    
    case_attribute = list(case_attribute_string.split(","))
    event_attribute = list(event_attribute_string.split(","))
    if case_attribute[0] == '$empty_string$':
        print("empty case attributes")
        case_attribute = list()
    if event_attribute[0] == '$empty_string$':
        print("empty case attributes")
        event_attribute = list()
    
    
    attributes_non_unique = case_attribute + event_attribute
    attributes_non_unique.append('Activity')
    attributes_non_unique.append('time:timestamp')
    
    attributes = list(set(attributes_non_unique)) 
    unique_identifier = ['Case ID']
    activity = ['Activity']
    timestamp = ['time:timestamp']

    
    current_file_name= ""
    #########################################
    for filename in os.listdir(filePath):
        if filename.endswith(".xes.csv"): 
            current_file_name= filename
            
    
    
    #df_data = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
    
    
    
    buffer_path = os.path.join(filePath, "buffer.csv")
    filePath = os.path.join(filePath, current_file_name)
    df_data = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
    #xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
    #if not 'Duration' in xes_csv_file.columns:
    #    xes_csv_file.loc[:,"Duration"] = 0.0
    ##########################################
    filePath = filePath.replace(" ","_")
    
    #if filePath.endswith(".xes"):
    #    log = xes_import_factory.apply(filePath)
    #    filePath = filePath + ".csv"
    #    csv_exporter.export(log, filePath)
    #targetFilePath = filePath.replace(".csv","_results")
    #run PRETSA
    #if filePath.endswith(".xes.csv"):
    #    xes_csv_file = pd.read_csv(filePath, delimiter=",",skipinitialspace=True, encoding="utf-8-sig")
    #    xes_csv_file.rename(columns={'concept:name': 'Activity', 'case:concept:name': 'Case ID'}, inplace=True)
    #    if not 'Duration' in xes_csv_file.columns:
    #        xes_csv_file.loc[:,"Duration"] = 0.0
    #    #xes_csv_file.to_csv(filePath,sep=";",encoding="utf-8-sig",index=False)
    
    #eventLog = pd.read_csv(filePath, delimiter=";",skipinitialspace=True, encoding="utf-8-sig")
    
    #######################
    ####csv2simple_auto####
    #######################
    
    # drop all unnecessary columns
    df_important_columns = df_data[unique_identifier + attributes]

    # group data by unique identifier
    df_grouped_by_identifier = df_important_columns.groupby(unique_identifier)

    # enumerate all data in their respective column
    df_enumerated_data = df_grouped_by_identifier.aggregate(lambda x: list(x))

    # create list to store data frames of each attribute
    list_of_data_frames = []

    list_column_names = []

    # insert constant values in the beginning, but respect given order
    # use this variable to determine the insertion position
    constant_value_count = 0

    # use attributes in file name
    list_file_name = []
    

    # loop through all variable attributes
    for attribute in attributes:
        # create data frame from list (from enumerated data)
        df_current_iteration = pd.DataFrame.from_records(list(df_enumerated_data[attribute]))

        # if attribute is constant only use it once and do not create multiple columns
        # determined by: count unique values for each row and drops 'None' values
        # if only the first column has a value or if all columns have the same value 'df.nunique' will
        # return '1'
        # if all 'df.nunique' returns for all rows '1' it will sum up to the number of rows
        # and therefore if those numbers are the same every row only contains one unique value
        if sum(df_current_iteration.nunique(dropna=True, axis=1)) == df_current_iteration.shape[0]:

            # get only first column. all other columns should either be empty or equal
            df_current_iteration = df_current_iteration.iloc[:, 0]

            # save it in a list of data frames
            list_of_data_frames.insert(constant_value_count, df_current_iteration)
            # create meaningful header, use the attribute name
            list_column_names.insert(constant_value_count, attribute.replace(" ", ""))

            # add attribute to filename
            list_file_name.insert(constant_value_count, attribute.replace(" ", ""))

            # increase insertion position by one
            constant_value_count += 1
        else:
            # save it in a list of data frames
            list_of_data_frames.append(df_current_iteration)
            # create meaningful header, use the attribute name and a number
            list_column_names.extend(np.core.defchararray.add(
                [attribute.replace(" ", "")] * list_of_data_frames[-1].shape[1],
                np.array(range(0, list_of_data_frames[-1].shape[1]), dtype=str)))
            list_file_name.append(attribute.replace(" ", ""))


    # concatenate separate data frames to one data frame
    df_for_export = pd.concat(list_of_data_frames, axis=1)

    # rename columns
    df_for_export.columns = list_column_names

    # get index (unique identifier) from enumerated data
    df_for_export.index = df_enumerated_data.index
    df_for_export.to_csv(buffer_path,sep=";")
    ###########################################################################################################################################################
    ###########################################################################################################################################################
    ###########################################################################################################################################################
    ###########################################################################################################################################################
    ###########################################################################################################################################################    
    pd.options.mode.chained_assignment = None   
    df_two = pd.read_csv(buffer_path, delimiter=";",low_memory=False, nrows=1000)   
    # Specify number or relative frequency of points
    number_points = 1    
    
    quasi_identifier, events_to_concat = generate_projection_view(projection, case_attribute, activity,
                                                                  event_attribute, timestamp)
    attributes_quasi = unique_identifier + quasi_identifier 
    
    df_aggregated_data = prepare_data(events_to_concat, df_two, attributes_quasi)
    print("Data preparation finished")
    
    unicity = calculate_unicity(df_aggregated_data, quasi_identifier, events_to_concat, number_points)
    print("unicity = ", unicity)
    
    
    ###########################################################################################################################################################
    result_filename = current_file_name.replace(".csv","_results.txt")
    puffer,targetFile = filePath.split("media"+os.path.sep)
    result_path = puffer +"media" +os.path.sep + secure_token +os.path.sep + result_filename
    targetFile = secure_token + os.path.sep + result_filename
    
    with open(result_path, 'w') as filehandle:
        filehandle.write("Unicity = %s \n" % unicity )
        filehandle.write("Based on activities \n")
        if projection == "1":
            filehandle.write("Timestamps \n")
        if projection == "2" or projection == "4":
            filehandle.write("Case attributes: \n")
            filehandle.writelines("%s\n" % cases for cases in case_attribute)
            filehandle.write("\n")
        if projection == "2" or projection == "3":
            filehandle.write("Event attributes: \n")
            filehandle.writelines("%s\n" % event_attr for event_attr in event_attribute)
        
    ###########################################################################################################################################################
    
    
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ?, docfile = ? WHERE token = ?", ("FINISHED", targetFile, secure_token))
    conn.commit()
    conn.close()
    print("DB submit done")

except:
    filePath = sys.argv[1]
    projection = sys.argv[2]
    case_attribute_string = sys.argv[3]
    event_attribute_string = sys.argv[4]
    dbName = sys.argv[5]
    secure_token = sys.argv[6]
    print()
    print("ERROR_except")
    print()
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("UPDATE eventlogUploader_document SET status = ? WHERE token = ?", ("ERROR", secure_token))
    conn.commit()
    conn.close()
