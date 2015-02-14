from __future__ import absolute_import
from multiprocessing import RLock, Array
import itertools
import logging
import time
import math

from hystrix.rolling_number import BucketCircular


log = logging.getLogger(__name__)


class RollingPercentile(object):

    def __init__(self, _time, milliseconds, bucket_numbers,
                 bucket_data_length, enabled):
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

    def mean(self):
        if not self.enabled:
            return -1

        # Force logic to move buckets forward in case other requests aren't
        # making it happen
        self.current_bucket()

        # Fetch the current snapshot
        return self.current_percentile_snapshot().mean()


class Bucket(object):
    ''' Counters for a given 'bucket' of time. '''

    def __init__(self, start_time, bucket_data_length):
        self.window_start = start_time
        self.data = PercentileBucketData(bucket_data_length)


class PercentileBucketData(object):

    def __init__(self, data_length):
        self.data_length = data_length
        self.list = Array('i', self.data_length, lock=RLock())
        # TODO: Change this to use a generator
        self.index = itertools.count()
        self.number = 0

    def add_value(self, *latencies):
        # We just wrap around the beginning and over-write if we go past
        # 'data_length' as that will effectively cause us to "sample" the
        # most recent data
        for latency in latencies:
            self.number = next(self.index)
            self.list[self.number % self.data_length] = latency
            self.number = self.number + 1

    def length(self):
        if self.number > len(self.list):
            return len(self.list)
        else:
            return self.number


class PercentileSnapshot(object):

    def __init__(self, *args):
        self.data = Array('i', 0, lock=RLock())
        self._mean = 0
        self.length = 0

        if isinstance(args[0], int):
            self.data = list(args)
            self.length = len(args)
            self.buckets = []

            _sum = 0
            for d in self.data:
                _sum += d

            self._mean = _sum / self.length
            self.data = Array('i', sorted(sorted(self.data), key=bool,
                                          reverse=True), lock=RLock())

        elif isinstance(args[0], Bucket):
            self.length_from_buckets = 0
            self.buckets = args
            for bucket in self.buckets:
                self.length_from_buckets += bucket.data.data_length

            self.data = Array('i', self.length_from_buckets, lock=RLock())
            _sum = 0
            index = 0
            for bucket in self.buckets:
                pbd = bucket.data
                length = pbd.length()
                for i in range(length):
                    v = pbd.list[i]
                    self.data[index] = v
                    index += 1
                    _sum += v

            self.length = index
            if self.length == 0:
                self._mean = 0
            else:
                self._mean = _sum / self.length

            self.data = Array('i', sorted(sorted(self.data), key=bool,
                                          reverse=True), lock=RLock())

    def percentile(self, percentile):
        if self.length == 0:
            return 0

        return self.compute_percentile(percentile)

    def compute_percentile(self, percent):
        if self.length <= 0:
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
