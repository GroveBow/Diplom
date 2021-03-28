import datetime

from flask import make_response

BASE_COMPLETE_TIME = datetime.datetime.strptime("1900-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')


def make_resp(message, status):
    resp = make_response(message, status)
    resp.headers['Content-type'] = 'application/json; charset=utf-8'
    return resp


def check_keys(dct, keys):
    return all(key in dct for key in keys)


def check_all_keys_in_dict(dct, keys):
    return all(key in keys for key in dct.keys())


def check_time_in_times(times, curr):
    return any(
        map(lambda s: s.start_time <= curr.start_time <= s.end_time or curr.start <= s.start_time <= curr.end_time, times))


def diff_time(time_a, time_b):
    end = (time_a.hour * 60 + time_a.minute) * 60 + \
          time_a.second
    start = (time_b.hour * 60 + time_b.minute) * 60 + \
            time_b.second
    return abs(end - start)
