import asyncio
import os

import airsim as ARS
import numpy as np

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
from kernel.process import PROCESS, subprocess

from .airsim_tools import AirSimTools

HELPER = AirSimTools()


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
        [-320.34, -206.58, 128.0],
        [-287.34, -179.58, 129.0],
        [-177.0, -132.35, 128.0],
        [-158.0, -121.9, 128.0],
        [-137.0, -110.35, 128.0],
        [-70.0, -73.5, 128.0],
        [120.0, 31.0, 128.0],
        [150.0, -23.55, 128.0],
        [120.0, 31.0, 128.0],
        [239.0, 96.45, 128.0],
    """

    PATH = [
        [4, 37.4, -6.8],
        [7, 62, -6.8],
        [2.234, 95.6, -6.8],
        [1.2, 123.6, -6.8],
        [1.2, 174.6, -6.8],
        [1.50, 225.1, -6.8],
        [-12, 307.4, -6.8],
        [1.50, 225.1, -6.8],
        [1.2, 174.6, -6.8],
        [1.2, 123.6, -6.8],
        [2.234, 95.6, -6.8],
        [7, 62, -6.8],
        [4, 37.4, -6.8],
        [0, 0, -6.8],
    ]
    """
    The path that the drone will follow.
    """
    RESOLUTION = {
        "144p": [256, 144],
        "240p": [426, 240],
        "360p": [640, 360],
        "480p": [854, 480],
        "720p": [1280, 720],
        "1080p": [1920, 1080],
        "1440p": [2560, 1440],
        "2160p": [3840, 2160],
        "4320p": [7680, 4320],
    }
    """
    The resolution of the video stream.
    """

    def _do_init(self):
        """
        This method initializes all the necessary AirSim configuration.
        """
        LOGGER.info(f"AirSim Do Init waiting for AirSim connection")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        beach_street_path = os.path.join(
            dir_path,
            "3d/ProjectOne/Binaries/Linux/ProjectOne",
        )
        LOGGER.debug(f"Beach Stret path: {beach_street_path}")
        assert os.path.exists(beach_street_path), "Beach Street should be installed"
        command = [
            beach_street_path,
            "-WINDOWED",
            "-ResX=1",
            "-ResY=1",
            "-RenderOffscreen",
        ]
        PROCESS.create_process(
            command,
            process_name="beach_street",
            stdout=subprocess.DEVNULL,  # subprocess.DEVNULL
            stderr=subprocess.DEVNULL,
        )
        self.speed = 0.5  # m/s
        # Wait for AirSim connection
        HELPER.airsim_connect()
        self.ini_epoch = HELPER.airsim_gettimestamp()
        HELPER.airsim_takeoff()
        HELPER.move_on_path(paths=self.PATH, speed=self.speed)  # speed = 0.5 m/s
        HELPER.pause()  # Pause the simulation and resume only in __execute_step
        self.index = 0
        """
        Prepare here the ffmpeg process to stream the drone
        video streaming. First, start the mediamtx server.
        """
        # Start media MTX server
        mtx = os.path.dirname(os.path.realpath(__file__)) + "/mediamtx/mediamtx"
        mtx_conf = (
            os.path.dirname(os.path.realpath(__file__)) + "/mediamtx/mediamtx.yml"
        )
        args = [mtx, mtx_conf]
        PROCESS.create_process(args, wait=False, process_name="mediamtx")
        reso = "720p"
        # Start ffmpeg process to stream video
        resolution = str(self.RESOLUTION[reso][0]) + "x" + str(self.RESOLUTION[reso][1])
        ffmpeg_command = [
            "ffmpeg",
            "-probesize",
            "4M",
            "-analyzeduration",
            "500000",
            "-framerate",
            "30",
            "-an",
            "-video_size",
            resolution,
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
            "-rtbufsize",
            "10M",
            "-x264-params",
            "keyint=10:min-keyint=10",
            "-tune",
            "zerolatency",
            "-f",
            "rtsp",
            "rtsp://localhost:8554/mystream",
        ]
        PROCESS.create_process(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            process_name="ffmpeg",
        )
        self.ffmpeg_process = PROCESS.get_process_by_name("ffmpeg")
        assert self.ffmpeg_process is not None, "ffmpeg process not created"
        self._start_streaming = False

    async def _execute_step(self):
        """
        This method executes the AirSim step.
        """
        LOGGER.debug(f"AirSim Execute Step")
        if HELPER.isPaused():
            HELPER.resume()

        """
        Since the granularity of the AirSim step is high, we need to
        limit the number of messages sent to sionna. We do this by
        sending a message every 125 ms. Avoiding, in the source,
        problems with backpressure and buffer overflow.
        """
        current_epoch = HELPER.airsim_gettimestamp()
        if ((current_epoch - self.ini_epoch) / 1e6) < 125:  # 125 ms
            return
        self.ini_epoch = current_epoch
        pose = HELPER.airsim_getpose()
        orientation = HELPER.airsim_getorientation()
        time_stap = HELPER.airsim_gettimestamp()
        if HELPER.airsim_getcollision():
            raise Exception("Collision detected")
        speed = np.linalg.norm(HELPER.airsim_getlinearvel())
        message = {
            "x-pos": float(pose[0]),
            "y-pos": float(pose[1]),
            "z-pos": float(pose[2]),
            "roll": float(orientation[0]),
            "pitch": float(orientation[1]),
            "yaw": float(orientation[2]),
            "speed": float(speed),
            "timestamp": int(time_stap),
        }
        # Send the message to sionna
        await NATS.send(self.__class__.__name__, message, "sionna")
        if not self._start_streaming:
            LOGGER.info("Starting video streaming")
            self._start_streaming = True
            # Start the video streaming
            asyncio.create_task(self.__start_video_streaming())

    async def __start_video_streaming(self):
        """
        Start the video streaming. This is done asynchronously to avoid blocking
        the main loop. The video is streamed outside the caviar scheduling. Unfortunately,
        the AirSim API does not provide a way to get the video frames in a non-blocking way.
        """
        while True:
            responses = HELPER.client.simGetImages(
                [ARS.ImageRequest(0, ARS.ImageType.Scene, False, False)]
            )  # raw bytes
            if self.ffmpeg_process.poll() is not None:
                raise Exception("ffmpeg process has stopped")
            if len(responses):
                image_response = responses[0]
                image_bytes = image_response.image_data_uint8
                self.ffmpeg_process.stdin.write(image_bytes)
                self.ffmpeg_process.stdin.flush()
            await asyncio.sleep(1 / 30)
