'''
This script can be used to parse out the timeseries data from the raw
files obtained from Intel
'''

import sys

import csv
import pickle
from datetime import datetime, timedelta

from timeseries import TimePoint, TimeSeries

def parse_header(header):

    #user,measure,timestamp-start,timestamp-end,value
    time_ind = header.index('timestamp-start')
    data_ind = header.index('value')

    return time_ind, data_ind

def parse_data_line(line,file_type,time_ind,data_ind):

    ''' Function to parse the data depending on the file type i.e. either
    tremor calls or movement data.'''

    time_point = datetime.strptime( line[time_ind], '%Y-%m-%d %H:%M:%S.%f')

    if file_type == 'tremor':
        # sc012l,Tremor Score,2016-03-29 19:18:55.000,,{Value=0.0}
        data_value = float(line[data_ind].split('=')[1].split('}')[0])

    elif file_type == 'movement':
        # sc012l,Pebble Accelerometer,2016-03-29 19:35:47.807,
        #         ,{z=-960.0, y=-120.0, x=-360.0}

        temp = line[data_ind:data_ind+3]
        temp = map(lambda x: x.strip('}').strip('{'), temp)
        data_value = map(lambda x: float(x.split('=')[1]), temp)
        data_value = list(data_value)

    else:
        raise typeerror('wrong file type. only "tremor" or \
                                                "movement" allowed')

    return time_point, data_value

def initialize_time_series(data_line,time_ind,data_ind,file_type,
                                                    series_name=None):

    TS = TimeSeries(name=series_name)
    date, value = parse_data_line(data_line,file_type,time_ind,data_ind)
    timepoint = TimePoint(date,value)
    TS.add_tp(timepoint)

    return TS

def parse_file(file_path,file_type,series_name=None):

    with open(file_path,'r',newline='') as csv_file:

        csv_data = csv.reader(csv_file)
        header = next(csv_data)
        time_ind, data_ind = parse_header(header)

        # Set the first time point object
        line = next(csv_data)
        TS = initialize_time_series(line,time_ind, data_ind,file_type,
                                                                series_name)
        line = next(csv_data)
        while line:
            try:
                date, value = parse_data_line(line,file_type,
                                                time_ind,data_ind)
                current_tp = TimePoint(date,value)
                TS.add_tp_to_end(current_tp)
                # Update the line
                line = next(csv_data)
            except StopIteration:
                break

    return TS
