from __future__ import absolute_import
from multiprocessing import RLock
import logging
import time
import math

from hystrix.rolling_number import BucketCircular

log = logging.getLogger(__name__)


class RollingPercentile(object):

    def __init__(self, _time, milliseconds, bucket_numbers, bucket_data_length, enabled):
        self.time = _time
        self.milliseconds = milliseconds
        self.buckets = BucketCircular(bucket_numbers)
        self.bucket_numbers = bucket_numbers
        self.bucket_data_length = bucket_data_length
        self.enabled = enabled
        self.snapshot = PercentileSnapshot(0)
        self._new_bucket_lock = RLock()

    def buckets_size_in_milliseconds(self):
        return self.milliseconds / self.bucket_numbers

    def current_bucket(self):
        current_time = self.time.current_time_in_millis()
        current_bucket = self.buckets.peek_last()

        if current_bucket is not None and current_time < (current_bucket.window_start + self.buckets_size_in_milliseconds()):
            return current_bucket

        with self._new_bucket_lock:
            # If we didn't find the current bucket above, then we have to
            # create one.
            if self.buckets.peek_last() is None:
                new_bucket = Bucket(current_time, self.bucket_data_length)
                self.buckets.add_last(new_bucket)
                return new_bucket
            else:
                for i in range(self.bucket_numbers):
                    last_bucket = self.buckets.peek_last()
                    if current_time < (last_bucket.window_start + self.buckets_size_in_milliseconds()):
                        return last_bucket
                    elif current_time - (last_bucket.window_start + self.buckets_size_in_milliseconds()) > self.milliseconds:
                        self.reset()
                        return self.current_bucket()
                    else:
                        all_buckets = [b for b in self.buckets]
                        self.buckets.add_last(Bucket(last_bucket.window_start + self.buckets_size_in_milliseconds(), self.bucket_data_length))
                        self.snapshot = PercentileSnapshot(*all_buckets)

                return self.buckets.peek_last()

        # we didn't get the lock so just return the latest bucket while
        # another thread creates the next one
        current_bucket = self.buckets.peek_last()
        if current_bucket is not None:
            return current_bucket
        else:
            # The rare scenario where multiple threads raced to create the
            # very first bucket wait slightly and then use recursion while
            # the other thread finishes creating a bucket
            time.sleep(5)
            self.current_bucket()

    def add_value(self, *values):
        ''' Add value (or values) to current bucket.
        '''

        if not self.enabled:
            return

        for value in values:
            self.current_bucket().data.add_value(value)

    def percentile(self, percentile):
        if not self.enabled:
            return -1

        # Force logic to move buckets forward in case other requests aren't
        # making it happen
        self.current_bucket()

        # Fetch the current snapshot
        return self.current_percentile_snapshot().percentile(percentile)

    def current_percentile_snapshot(self):
        return self.snapshot


class Bucket(object):
    ''' Counters for a given 'bucket' of time. '''

    def __init__(self, start_time, bucket_data_length):
        self.window_start = start_time
        self.data = PercentileBucketData(bucket_data_length)


class PercentileBucketData(object):

    def __init__(self, data_length):
        self.length = data_length
        self.list = []

    def add_value(self, *latencies):
        for latency in latencies:
            self.list.append(latency)

    def length(self):
        return len(self.list)


class PercentileSnapshot(object):

    def __init__(self, *args):
        self.data = []
        self._mean = 0

        if isinstance(args[0], int):
            self.data = list(args)
            self.length = len(args)
            self.buckets = []

            _sum = 0
            for d in self.data:
                _sum += d

            self._mean = _sum / self.length

        elif isinstance(args[0], Bucket):
            self.buckets = args
            _sum = 0
            for bucket in self.buckets:
                pbd = bucket.data
                self.data.extend(pbd.list)
                for l in pbd.list:
                    _sum += l

            self.length = len(pbd.list)
            if self.length == 0:
                self._mean = 0
            else:
                self._mean = _sum / self.length

        self.data.sort()

    def percentile(self, percentile):
        if not self.length:
            return 0

        return self.compute_percentile(percentile)

    def compute_percentile(self, percent):
        if not self.length:
            return 0
        elif percent <= 0.0:
            return self.data[0]
        elif percent >= 100.0:
            return self.data[self.length - 1]

        rank = (percent / 100.0) * self.length

        # Linear interpolation between closest ranks
        ilow = int(math.floor(rank))
        ihigh = int(math.ceil(rank))

        assert 0 <= ilow and ilow <= rank and rank <= ihigh and ihigh <= self.length
        assert (ihigh - ilow) <= 1

        if ihigh >= self.length:
            # Another edge case
            return self.data[self.length - 1]
        elif ilow == ihigh:
            return self.data[ilow]
        else:
            # Interpolate between the two bounding values
            return int(self.data[ilow] + (rank - ilow) * (self.data[ihigh] - self.data[ilow]))

    def mean(self):
        return int(self._mean)
