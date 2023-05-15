import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pynats import NATSClient

# from examples.sionna.followPath import sionnaStart, sionnaStop
# from examples.sionna.execute_run import run as sionnaRun
import json


class CaviarEnv(gym.Env):
    def __init__(self):
        ################ Enables communication with the other subsystems #######
        with NATSClient() as natsclient:
            self.natsclient = natsclient
            self.natsclient.subscribe(
                subject="caviar.comm.rxpositionandbestray",
                callback=self._receiveCommInfo,
            )
            print("Waiting")
            natsclient.wait(count=1)
        ########################################################################
        self.nTx = 32  # Number of transmitters
        self.nRx = 8  # Number of receivers
        self.number_of_beam_pairs = self.nTx * self.nRx
        # The observation is defined as a three dimensional list of float
        # values representing the drone position in cartesian coordinates
        # (i.e [10, 20, 50])
        self.obs_space = spaces.Box(low=-500, high=500, shape=(3, 1), seed=1)
        # The action space is composed by a singular integer value within
        # a range of [0, 255] representing one of the possible beam pairs
        self.act_space = spaces.Discrete(self.number_of_beam_pairs)
        self.done = False

    def reset(self):
        self.natsclient.close()
        self.done = False
        observation = np.array([0, 0, 0])
        return observation

    # def step(self):
    #     return observation, reward, self.done, info

    def _receiveCommInfo(self, msg):
        payload = json.loads(msg.payload.decode())
        print(payload["best_ray"])


if __name__ == "__main__":
    env = CaviarEnv()
