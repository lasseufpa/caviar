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

        # Start media MTX server
        mtx = os.path.dirname(os.path.realpath(__file__)) + "/mediamtx/mediamtx"
        mtx_conf = (
            os.path.dirname(os.path.realpath(__file__)) + "/mediamtx/mediamtx.yml"
        )
        args = [mtx, mtx_conf]
        PROCESS.create_process(args, wait=False, process_name="mediamtx")

        # Start ffmpeg process to stream video
        ffmpeg_command = [
            "ffmpeg",
            "-probesize",
            "32M",  # Look at up to 32 megabytes of data
            "-analyzeduration",
            "1000000",
            "-framerate",
            "10",
            "-video_size",
            "256x144",
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
        await NATS.send(self.__class__.__name__, message, "sionna")
        # HELPER.pause()

        responses = HELPER.client.simGetImages(
            [ARS.ImageRequest(0, ARS.ImageType.Scene, False, False)]
        )  # raw bytes
        if len(responses):
            image_response = responses[0]
            # TODO: MAYBE SEND THESE BYTES TO ns-3, since the transmission will occur in ns-3 block
            image_bytes = image_response.image_data_uint8
            self.ffmpeg_process.stdin.write(image_bytes)
            self.ffmpeg_process.stdin.flush()
