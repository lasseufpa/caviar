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
        [4, 37.4, -7.8],
        [7, 62, -7.8],
        [2.234, 95.6, -7.8],
        [1.2, 123.6, -7.8],
        [1.2, 174.6, -7.8],
        [4.0, 225.1, -7.8],
        [-12, 307.4, -7.8],
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

        # Wait for AirSim connection
        HELPER.airsim_connect()
        HELPER.airsim_takeoff()
        HELPER.move_on_path(paths=self.PATH, speed=0.50)  # speed = 0.5 m/s
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
        reso = "144p"
        # Start ffmpeg process to stream video
        resolution = str(self.RESOLUTION[reso][0]) + "x" + str(self.RESOLUTION[reso][1])
        ffmpeg_command = [
            "ffmpeg",
            "-probesize",
            "32M",  # Look at up to 32 megabytes of data
            "-analyzeduration",
            "1000000",
            "-framerate",
            "10",
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
            "ultrafast",
            "-tune",
            "zerolatency",
            "-f",
            "rtsp",
            "rtsp://localhost:8554/mystream",
        ]
        PROCESS.create_process(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            process_name="ffmpeg",
        )
        self.ffmpeg_process = PROCESS.get_process_by_name("ffmpeg")
        assert self.ffmpeg_process is not None, "ffmpeg process not created"

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
        sending a message every 25 steps. Avoiding in the source
        problems with backpressure and buffer overflow.
        """
        self.index += 1
        if not self.index % 50 == 0:
            return
        pose = HELPER.airsim_getpose()
        if HELPER.airsim_getcollision():
            raise Exception("Collision detected")
        speed = np.linalg.norm(HELPER.airsim_getlinearvel())
        message = {
            "x-pos": float(pose[0]),
            "y-pos": float(pose[1]),
            "z-pos": float(pose[2]),
            "speed": float(speed),
        }
        # Send the message to sionna
        await NATS.send(self.__class__.__name__, message, "sionna")

        responses = HELPER.client.simGetImages(
            [ARS.ImageRequest(0, ARS.ImageType.Scene, False, False)]
        )  # raw bytes
        if len(responses):
            image_response = responses[0]
            image_bytes = image_response.image_data_uint8
            self.ffmpeg_process.stdin.write(image_bytes)
            self.ffmpeg_process.stdin.flush()
