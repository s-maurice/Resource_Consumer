import time
from asyncio import sleep


class BaseRateHandler(object):
    # await-able rate handler that averages out the previous n times
    # to variably wait to keep rate at a target value

    average_n_times = 10  # average the previous n frame or tick times
    minimum_time = 0.002  # minimum time for the await between frames or ticks

    def __init__(self, rate_target_per_second, display_performance=False):
        self.rate_target = rate_target_per_second
        self.rate_target = 1 / rate_target_per_second

        self.current_period_start = None
        self.previous_period_times = []

        self.display_performance = display_performance

    def period_start(self):
        # called at the beginning of a frame
        self.current_period_start = time.time()

    async def period_end(self):
        # called at the end of a frame, also halts for the correct time
        assert self.current_period_start is not None  # frame_start() needs to be called before frame_end()

        current_frame_time = time.time() - self.current_period_start

        if self.display_performance:
            print("Time taken for last period: ", current_frame_time)

        self.previous_period_times.append(current_frame_time)
        # remove the first item in the list
        if len(self.previous_period_times) > self.average_n_times:
            self.previous_period_times.pop(0)

        average_period_time = sum(self.previous_period_times) / len(self.previous_period_times)  # in seconds

        wait_time = self.rate_target - average_period_time
        wait_time = max(wait_time, self.minimum_time)

        await sleep(wait_time)  # asyncio.sleep()


class FrameRateHandler(BaseRateHandler):
    average_n_times = 10  # average the previous n frame or tick times
    minimum_time = 0.002  # minimum time for the await between frames or ticks


class NetworkRateHandler(BaseRateHandler):
    average_n_times = 10  # average the previous n frame or tick times
    minimum_time = 0.002  # minimum time for the await between frames or ticks


class GameRateHandler(BaseRateHandler):
    average_n_times = 10  # average the previous n frame or tick times
    minimum_time = 0.002  # minimum time for the await between frames or ticks
