import os

import airsim as ARS

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
from kernel.process import PROCESS, subprocess

from .airsim_tools import AirSimTools

HELPER = AirSimTools()


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
    """

    PATH = [
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
        # Wait for AirSim connection
        HELPER.airsim_connect()
        HELPER.airsim_setpose(x=-320.34, y=-206.58, z=135)
        HELPER.airsim_takeoff()
        HELPER.move_on_path(paths=self.PATH, speed=0.80)  # speed = 0.8 m/s
        HELPER.pause()  # Pause the simulation and resume only in __execute_step

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

        # Start ffmpeg process to stream video
        resolution = (
            str(self.RESOLUTION["144p"][0]) + "x" + str(self.RESOLUTION["144p"][1])
        )
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
        if HELPER.isPaused():
            HELPER.resume()

        LOGGER.debug(f"AirSim Execute Step")
        # HELPER.resume()
        pose = HELPER.airsim_getpose()
        print(f"Pose: {pose}")
        if HELPER.airsim_getcollision():
            raise Exception("Collision detected")

        message = {
            "x-pos": float(pose[0]),
            "y-pos": float(pose[1]),
            "z-pos": float(pose[2]),
            "speed": 5.0,
        }
        # Send the message to ns-3 and sionna
        await NATS.send(self.__class__.__name__, message, "sionna")
        await NATS.send(self.__class__.__name__, message, "ns3")
        responses = HELPER.client.simGetImages(
            [ARS.ImageRequest(0, ARS.ImageType.Scene, False, False)]
        )  # raw bytes
        if len(responses):
            image_response = responses[0]
            image_bytes = image_response.image_data_uint8
            self.ffmpeg_process.stdin.write(image_bytes)
            self.ffmpeg_process.stdin.flush()
