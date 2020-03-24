import time
from asyncio import sleep


class FramerateHandler(object):
    # await-able framerate handler that averages out the previous n frame-times
    # to variably wait to keep framerate at a target value
    def __init__(self, framerate_target):
        self.framerate_target = framerate_target
        self.frametime_target = 1 / framerate_target

        self.current_frame_start = None
        self.previous_frame_times = []
        self.average_n_frame_times = 10  # averages the previous 10 frame times
        self.minimum_frametime = 0.005  # minimum time for the await between frames

    def frame_start(self):
        # called at the beginning of a frame
        self.current_frame_start = time.time()

    async def frame_end(self):
        # called at the end of a frame, also halts for the correct time
        assert self.current_frame_start is not None  # frame_start() needs to be called before frame_end()

        current_frame_time = time.time() - self.current_frame_start

        self.previous_frame_times.append(current_frame_time)
        # remove the first item in the list
        if len(self.previous_frame_times) > self.average_n_frame_times:
            self.previous_frame_times.pop(0)

        average_frame_time = sum(self.previous_frame_times) / len(self.previous_frame_times)  # in seconds

        wait_time = self.frametime_target - average_frame_time
        wait_time = max(wait_time, self.minimum_frametime)

        await sleep(wait_time)  # asyncio.sleep()
