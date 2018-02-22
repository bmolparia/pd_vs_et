from ..timeseries import *

a = TimePoint(time=1,value=2)
b = TimePoint(time=3,value=4)
c = TimePoint(time=4,value=5)

a.next_tp = b
b.last_tp = a
b.next_tp = c
c.last_tp = b

tps = [a,b,c]
TS = TimeSeries(tps)

def test_timepoint():
    'Tests TimePoint attributes'

    assert a.value == 2
    assert a.next_time == 2
    assert a.last_time == None
    assert b.value == 4
    assert b.next_time == 1
    assert b.last_time == 2
    assert c.value == 5
    assert c.next_time == None
    assert c.last_time == 1

def test_time_series():
    'Tests TimeSeries attributes'

    assert len(TS) == 3
    assert TS.duration == c.time - a.time

def test_time_series_element_addition():
    'Tests TimeSeries attributes'

    d = TimePoint(time=2,value=6)
    TS.add_tp(d)

    assert d in TS
    assert TS[1] == d

    e = TimePoint(time=5,value=7)
    TS.add_tp_to_end(e)

    assert TS[-1] == e
    assert TS.duration == (e.time - a.time)

    f = TimePoint(time=0,value=7)
    TS.add_tp_to_beginning(f)

    assert TS[0] == f
    assert TS.duration == (e.time - f.time)
    assert len(TS) == 6
    assert TS.values == [f,a,d,b,c,e]

def test_edge_condition_adding():
    'Tests adding to empty TimeSeries object'
    TS = TimeSeries()
    TS.add_tp_to_end(a)
    assert TS[0] == a

    TS.add_tp_to_end(b)
    assert TS.values == [a,b]

    TS = TimeSeries()
    TS.add_tp_to_beginning(b)
    assert TS[0] == b

    TS.add_tp_to_beginning(a)
    f = TimePoint(time=0,value=7)
    TS.add_tp_to_beginning(f)
    assert TS.values == [f,a,b]

def test_time_slice():
    'Tests slicing functions'

    time_points = [TimePoint(time=x,value=x) for x in range(100)]
    TS = TimeSeries()
    for t in time_points:
        TS.add_tp_to_end(t)

    start_tp = time_points[37]
    forward_slice = TS.get_time_slice_forward(start_tp, 13)
    reverse_slice = TS.get_time_slice_reverse(start_tp, 13)

    for_duration = forward_slice[-1].time - forward_slice[0].time
    rev_duration = reverse_slice[-1].time - reverse_slice[0].time

    print(forward_slice)
    print(reverse_slice)

    assert for_duration == 13
    assert rev_duration == 13
    assert len(forward_slice) == 14
    assert len(reverse_slice) == 14

    assert forward_slice[0] == start_tp
    assert reverse_slice[-1] == start_tp
