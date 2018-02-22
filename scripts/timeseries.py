'''
This script describes an object to store TimeSeries data.
'''

from sorted_collection import SortedCollection

class TimePoint(object):

    def __init__(self, time, value, last_tp=None, next_tp=None):

        self.time = time
        self.value = value
        self._next_tp = next_tp
        self._last_tp = last_tp
        self.next_time = None
        self.last_time = None

        if next_tp != None:
            self.next_time = self.next_tp.time - self.time
        if last_tp != None:
            self.last_time = self.time - self.last_tp.time

    def __str__(self):
        return '(time:{}, value:{})'.format(self.time, self.value)

    def __repr__(self):
        return str(self)

    @property
    def next_tp(self):
        return self._next_tp

    @next_tp.setter
    def next_tp(self,value):
        "Defines the set attribute function for the next time point. Raise \
        TypeError if value isn't a TimePoint object."
        try:
            assert( isinstance(value, TimePoint))
        except AssertionError:
            raise TypeError('next_tp has to be a TimePoint object')

        self._next_tp = value
        self.next_time = self.next_tp.time - self.time

    @property
    def last_tp(self):
        return self._last_tp

    @last_tp.setter
    def last_tp(self,value):
        "Defines the set attribute function for the previous time point.Raise \
        TypeError if value isn't a TimePoint object."
        try:
            assert( isinstance(value, TimePoint))
        except AssertionError:
            raise TypeError('last_tp has to be a TimePoint object')

        self._last_tp = value
        self.last_time = self.time - self.last_tp.time


class TimeSeries(SortedCollection):

    def __init__(self,iterable=(),name=None):
        super().__init__(iterable=iterable, key=lambda x: x.time)
        self.name = name
        self.values = self._items
        self.times = self._keys
        self._duration = None

    def __str__(self):
        return '{}: {} timepoints spanning {} '.format(self.name, len(self),
                                                                self.duration)

    def __repr__(self):
        return str(self)

    @property
    def duration(self):
        return self._duration

    @duration.getter
    def duration(self):
        return (self._keys[-1] - self._keys[0])

    def add_tp(self,tp):

        self.insert(tp)
        tp_index = self.index(tp)
        if tp_index > 0:
            last_tp = self[tp_index-1]
            tp.last_tp = last_tp
            last_tp.next_tp = tp
        try:
            next_tp = self[tp_index+1]
            tp.next_tp = next_tp
            next_tp.last_tp = tp
        except IndexError:
            pass

    def add_tp_to_end(self,tp):
        'Add a time point object at the end of the timeseries.'

        if len(self) == 0:
            self._keys.insert(0,tp.time)
            self._items.insert(0,tp)
        else:
            ins_pos = len(self)
            last_tp_index = ins_pos-1

            if self._keys[last_tp_index] < tp.time:

                self._keys.insert(ins_pos, tp.time)
                self._items.insert(ins_pos, tp)

                last_tp = self[last_tp_index]
                tp.last_tp = last_tp
                last_tp.next_tp = tp

            else:
                raise Exception('Time must be more than the last time stored.')

    def add_tp_to_beginning(self,tp):
        'Add a time point object at the beginning of the timeseries.'

        if len(self) == 0:
            self._keys.insert(0,tp.time)
            self._items.insert(0,tp)
        else:
            ins_pos = 0
            next_tp_index = 0

            if self._keys[next_tp_index] > tp.time:

                self._keys.insert(ins_pos, tp.time)
                self._items.insert(ins_pos, tp)

                next_tp = self[next_tp_index]
                tp.next_tp = next_tp
                next_tp.last_tp = tp
            else:
                raise Exception('Time must be less than the first time stored.')

    def get_time_slice_forward(self,start_tp,time_period):
        'Get a list of  all the timepoints starting at specified time and \
        ending after a given time period.'

        # Initilize
        time_slice = [start_tp]
        current_tp = start_tp
        duration = current_tp.next_time

        while duration <= time_period:
            next_tp = current_tp.next_tp
            time_slice.append(next_tp)
            current_tp = next_tp

            if current_tp.next_tp == None:
                break
            duration += current_tp.next_time

        return time_slice

    def get_time_slice_reverse(self,start_tp,time_period):
        'Get a list of  all the timepoints starting at specified time and \
        ending after a given time period in the reserse direction.'

        # Initilize
        time_slice = [start_tp]
        current_tp = start_tp
        duration = current_tp.last_time

        while duration <= time_period:
            last_tp = current_tp.last_tp
            time_slice.insert(0,last_tp)
            current_tp = last_tp

            if current_tp.last_tp == None:
                break
            duration += current_tp.last_time

        return time_slice

    def to_dict(self):
        'Get a dictionary of _keys and _items as keys and values of a dict'

        return {x:y for x,y in zip(self._keys,self._items)}
