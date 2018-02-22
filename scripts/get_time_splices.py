import argparse
import pickle
from datetime import timedelta, datetime
import numpy as np
from numpy import linalg as LA

from parse_data import parse_file

def get_5second_slice(tseries,start_tp):
    '''Get all the time points 5 seconds before the given time point.'''

    tdelta = timedelta(seconds=5)
    tslice = tseries.get_time_slice_reverse(start_tp,tdelta)

    return tslice

def get_gameplays(tseries):
    ''' Generates continuous timeseries of duration about 2 mins. Continuous
    being time points within 1 second of each other.'''

    end = False
    current_tp = tseries[0]
    duration = timedelta(0)
    gameplay = [current_tp]

    while not end:

        next_tp = current_tp.next_tp
        time_gap = current_tp.next_time

        if time_gap < timedelta(seconds=2):
            duration += current_tp.next_time
            gameplay.append(next_tp)
        else:
            if duration>timedelta(minutes=1.5) and duration<timedelta(minutes=5):
                yield gameplay

            gameplay = [next_tp]
            duration = timedelta(0)

        if next_tp.next_time == None:
            end = True

        current_tp = next_tp

def get_gameplays_with_time_stamp(tseries,time_stamps):
    ''' This function pulls out the last 5 minutes of gameplay data for every
    time point in the given time_stamps.
    It's possible that records of gameplays exist for times at which movement
    data isn't available. Therefore, only select gameplays that are less than 5
    minutes from the record time stamp.
    '''

    duration = timedelta(minutes=5)

    time_stamps = np.array(time_stamps)
    time_stamps = time_stamps/1e3
    convert_to_time = np.vectorize(datetime.utcfromtimestamp)
    time_stamps = convert_to_time(time_stamps)
    error_file = tseries.name+'.err.txt'

    for time_stamp in time_stamps:

        try:
            time_point = tseries.find_le(time_stamp)

            # time point can't be more than 5 minutes away from
            # the record time stamp
            time_from_patient_response = time_stamp - time_point.time
            if time_from_patient_response < timedelta(minutes=5):
                gameplay = tseries.get_time_slice_reverse(start_tp=time_point,
                                                        time_period=duration)
                yield gameplay
            else:
                with open(error_file,'a') as err:
                    err.write(repr(time_stamp)+'\n')

        except ValueError as e:
            print(e)


def get_magnitudes(array):
    '''Convert 3D vector data to magnitudes.
    Input is an array of time points.'''

    vector_points = np.array(list(map(lambda x: x.value, array)))
    magnitudes = LA.norm(vector_points,axis=1)
    magnitudes = magnitudes.tolist()

    return magnitudes


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This script can be used \
    to read in raw files from Intel and store them as TimeSeries objects.')
    parser.add_argument('mfile',metavar='Movement File',help='path to movement \
    data file')
    parser.add_argument('outfile',metavar='Output File',help='path to output \
    file')
    parser.add_argument('--tsfile',dest='tsfile',action='store',default=None,
                        help='File containing time stamps for questionnaires\
    answered. This has to be a pickle file containing a list of time stamps.')

    args = parser.parse_args()
    sample_name = args.mfile.split('/')[-1]
    movements = parse_file(args.mfile,'movement',series_name=sample_name)

    if args.tsfile != None:

        with open(args.tsfile,'rb') as inp:
            time_stamps = pickle.load(inp)

        ind = 1
        for gameplay in get_gameplays_with_time_stamp(movements,time_stamps):
            pass
            fname = args.outfile+'_'+str(ind)+'.pickle'
            magnitudes = get_magnitudes(gameplay)
            ind += 1

            with open(fname,'wb') as out:
                pickle.dump(magnitudes,out)

    else:
        ind = 1
        for gameplay in get_gameplays(movements):
            fname = args.outfile+'_'+str(ind)+'.pickle'
            magnitudes = get_magnitudes(gameplay)
            ind += 1

            print(fname)
            with open(fname,'wb') as out:
                pickle.dump(magnitudes,out)
