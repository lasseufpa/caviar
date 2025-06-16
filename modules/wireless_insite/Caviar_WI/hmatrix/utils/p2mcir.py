import collections

import numpy as np

from .p2mdoa import P2mFileParser

class P2mCir(P2mFileParser):
    """Parse a p2m cir file"""

    def _parse_receiver(self):
        """Get receiver and number of paths (pair Tx-Rx)"""
        line = self._get_next_line()
        receiver, n_paths = [int(i) for i in line.split()]
        self.data[receiver] = collections.OrderedDict()
        self.data[receiver]['paths_number'] = n_paths
        if n_paths == 0:
            self.data[receiver] = None
            return
        """Read: phase, arrival_time and power of a ray"""
        for rays in range(n_paths):
            line = self._get_next_line()
            ray_n, phase, arrival_time, srcvdpower = [float(i) for i in line.split()]
            self.data[receiver][ray_n] = collections.OrderedDict()
            self.data[receiver][ray_n]['ray_n'] = ray_n
            self.data[receiver][ray_n]['phase'] = phase
            self.data[receiver][ray_n]['arrival_time'] = arrival_time
            self.data[receiver][ray_n]['srcvdpower'] = srcvdpower
            
    def get_phase_ndarray(self, antenna_number):
        '''Returns all phases in degrees. antenna_number starts with 1 (not 0).'''
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'],))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths+1]['phase']
        return data_ndarray
        
if __name__=='__main__':
    #cir  = P2mCir('../example/model.cir.t001_01.r002.p2m')
    cir  = P2mCir('/mnt/d/github/5gm-rwi-simulation/example/results_new_simuls/run00001/study/model.cir.t001_01.r002.p2m')
    print('Phases in degrees: ', cir.get_phase_ndarray(1)) #Pass the antenna_number as argument starting in 1
    print('Phases in degrees: ', cir.get_phase_ndarray(10)) #Pass the antenna_number as argument starting in 1
