import pandas as pd
import glob
from datetime import datetime
import os
import csv
import random
import sys
csv.field_size_limit(sys.maxsize)

ride_id = 0
def merge_files(directory_path):
    merged_data = []
    #find all files starting with "VM" in the directory and all subdirectories
    files = glob.glob(directory_path + '/**/VM*', recursive=True)
    file_count = 0
    merge_count = 0
    ride_id = 0
    for filename in files:
        if filename.__contains__("Profiles"):
            continue
        with open(filename, 'r') as file:
            rider_id = random.randint(1, 30)
            count = 0
            for line in file:
                if line.startswith("lat"):
                    break
                count+=1
            file_data = file.readlines()[count:]
            reader = csv.reader(file_data)
            data = list(reader)
            # create skipper variable to ignore already interpolated data
            skipper = -1
            for i in range(0, len(data)):
                if i >= skipper:
                    if data[i][0] and data[i][1]:
                        for j in range (i, len(data)):
                            if j-i > 1:
                                if data[j][0] and data[j][1]:
                                    skipper = j
                                    start_val0= float(data[i][0])
                                    end_val0 = float(data[j][0])
                                    start_val1= float(data[i][1])
                                    end_val1 = float(data[j][1])
                                    diff0 = end_val0 - start_val0
                                    diff1 = end_val1 - start_val1
                                    num_rows = j-i
                                    increment0 = diff0 / (num_rows)
                                    increment1 = diff1 / (num_rows)
                                    for k in range(1, num_rows):
                                        value0 = round(start_val0 + k * increment0,8)
                                        value1 = round(start_val1 + k * increment1,8)
                                        data[i+k][0] = str(value0)
                                        data[i+k][1] = str(value1)
                                    break  
            for i in range(0, len(data)):
                if not data[i][0] and not data[i][1]:
                    data [i] = ""
                #shift all data in list 2 spaces to right and fill first two spaces with data from ride_id and rider_id
                else:
                    data[i] = [ride_id, rider_id] + data[i]

            
            # Append the data to the merged_data list
            merged_data.extend(data)
            #write to global variable
            ride_id +=1

            if file_count < 200:
                file_count += 1
            else: 
                with open('merged0'+str(merge_count)+'.csv', 'w', newline='') as write_file:
                    writer = csv.writer(write_file)
                    writer.writerows(merged_data)
                    print("Wrote data to merged0"+str(merge_count)+".csv")
                    file_count = 0
                    merge_count += 1
                    merged_data = []
    if file_count != 0:
        with open('merged0'+str(merge_count)+'.csv', 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(merged_data)
            print("Wrote data to merged0"+str(merge_count)+".csv")
            file_count = 0
            merge_count += 1
            merged_data = []

    # Write the merged data to a new CSV file with comma as the delimiter

def trim_csv_files():
    # get all files in the folder starting with merged, but only in the top level directory
    files = glob.glob('merged*')
    print(len(files))
    for input_file in files:
        print(f'Trimming file: {input_file}')
        (pd.read_csv(input_file, delimiter=',', header=None, skip_blank_lines=True, usecols= range(8) )).to_csv(input_file, index=False, header= None)
def convert_timestamp():
    # Read the csv file
    files = glob.glob('merged*')
    for input_file in files:
        df = pd.read_csv(input_file, header= None)

        # Convert the timestamp to a human readable format
        df[7] = pd.to_datetime(df[7], unit='ms')

        # Write the trimmed dataframe to a new csv file
        df.to_csv(input_file, index=False, header= None)

def create_trip_data():
    # Read the file into a dataframe
    files = glob.glob('merged*')
    for input_file in files:
        print(f'Creating trip data for {input_file}')
        df = pd.read_csv(input_file)
        output_rows = []
        ride_id = -1
        rider_id = -1
        tgeompoint = ""
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        for line in df.values:
            # check if ride_id and rider_id are -1, i.e the first line
            if ride_id == -1 and rider_id == -1:
                ride_id = line[0]
                rider_id = line[1]
                tstamp = datetime.strptime("2000-11-29 18:11:25.000",date_format)
                tgeompoint = "{["
                #get timestamp and store it in tstamp
            # check if ride_id matches the first value in the line
            if ride_id == line[0]:
                cstamp=datetime.strptime(line[7],date_format)
                # only append if the timestamp is greater than the previous timestamp
                if  cstamp > tstamp:
                    tgeompoint += f"Point({line[2]} {line[3]})@{line[7]}, "
                    tstamp = cstamp
                else:
                    continue
            else:
                #end the line, and start a new one after appending this to the final data
                #remove the last value from the tgeompoint string, and append ]}' to the end
                tgeompoint = tgeompoint[:-2] + "]}"
                output_rows.append([ride_id, rider_id, tgeompoint])
                ride_id = line[0]
                rider_id = line[1]
                tgeompoint = "{["
                tgeompoint += f"Point({line[2]} {line[3]})@{line[7]}, "
                tstamp = datetime.strptime(line[7], date_format)
        tgeompoint = tgeompoint[:-2] + "]}"
        output_rows.append([ride_id, rider_id, tgeompoint])
        output_df = pd.DataFrame(output_rows, columns=['ride_id', 'rider_id', 'tgeompoint'])
        # Write the output dataframe to a new CSV file, which takes the last character from the file name and adds it to trips, resulting in trips1 as an example
        
        # don't double quote strings in the output file while keeping the rest the same
        output_df.to_csv('trips_' + input_file, index=False, quoting=3, escapechar='\\', sep = ';')
    
def create_geomesa_data():
    #convert all spaces found in the file to "T"
    files = glob.glob('merged*')
    for input_file in files:
        output_file = 'geomesa_' + input_file
        with open(input_file, 'r') as file:
            filedata = file.read()
            filedata = filedata.replace(" ", "T")
        with open(output_file, 'w') as file:
            file.write(filedata)
        print(f'Geomesa data written to {output_file}')

def create_geomesa_trip_data():
    #convert all spaces found in the file to "T"
    files = glob.glob('geomesa_merged*')
    for input_file in files:
        output_file = 'geomesa_trips_' + input_file
        ride_id = ""
        rider_id = ""
        time_list = "\""
        multiline = "MULTILINESTRING("
        add_string = "("
        with open(input_file, 'r') as file:
            write_data = ""
            #read as csv file
            print(input_file)
            filedata = csv.reader(file, delimiter=',')
            for line in filedata:
                #handle first line
                if ride_id == "":
                    ride_id = line[0]
                    rider_id = line[1]
                    add_string = f"{line[3]} {line[2]},"
                    time_list+= f"{line[7]}, "
                    continue
                elif ride_id == line[0]:
                    add_string += f"{line[3]} {line[2]},"
                    time_list+= f"{line[7]}, "
                else:
                    #finish the strings and arrays, write them, and then empty them
                    #remove the last char from lat_string and long_string
                    add_string = add_string[:-1]+")"
                    time_list = time_list[:-2]+"\""
                    string_to_write = multiline + add_string+")"
                    write_data = f"{ride_id};{rider_id};{string_to_write};{time_list}\n"
                    
                    with open(output_file, 'a') as file:
                       file.write(write_data)
                    ride_id = line[0]
                    rider_id = line[1]
                    time_list = "\""
                    add_string = "("
                    write_data = ""
            #write the last lines after file ends
            add_string = add_string[:-1]+")"
            time_list = time_list[:-2]+"\""
            string_to_write = multiline + add_string+")"
            write_data = f"{ride_id};{rider_id};{string_to_write};{time_list}\n"
            with open(output_file, 'a') as file:
                file.write(write_data)
        print(f'Geomesa trip data written to {output_file}')
        
def create_postgis_trip_data():
    files = glob.glob('geomesa_trips*')
    for input_file in files:
        output_file = 'postgis_trips_' + input_file[-12:]
        with open(input_file, 'r') as file:
            write_data = ""
            #read as csv file
            filedata = csv.reader(file, delimiter=';')
            for line in filedata:
                timearray = "{"+line[3]+"}"
                #write the data to the new file
                write_data += f"{line[0]};{line[1]};{line[2]};{timearray}\n"
            with open(output_file, 'a') as file:
                file.write(write_data)

#merge_files("SimRa")
#trim_csv_files()
#convert_timestamp()
#create_geomesa_data()
#create_trip_data()
#create_geomesa_trip_data()
create_postgis_trip_data()
