'''
Change log:
AK - April 19, 2019 - provided support to InSite version 3.3, which includes path phase into p2m file.
'''
import collections

import numpy as np

from .p2mdoa import P2mFileParser

class P2mPaths(P2mFileParser):
    """Parse a p2m paths file"""

    def _parse_receiver(self):
        """Get receiver and number of paths (pair Tx-Rx)"""
        line = self._get_next_line()
        receiver, n_paths = [int(i) for i in line.split()]
        self.data[receiver] = collections.OrderedDict() #note we use a dictionary (hash table) to store information
        if n_paths == 0:
            self.data[receiver] = None
            return
        """Read: received_power -self.data[receiver][0]-, arrival_time -self.data[receiver][1]-,
         spread_delay -self.data[receiver][2]-"""
        #These are statistics per receiver (accounts for all paths)
        line = self._get_next_line()
        received_power, arrival_time, spread_delay = [float(i) for i in line.split()]
        self.data[receiver]['received_power'] = received_power
        self.data[receiver]['arrival_time'] = arrival_time
        self.data[receiver]['spread_delay'] = spread_delay
        self.data[receiver]['paths_number'] = n_paths
        """Read for version 3.2: srcvdpower, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2"""
        """or read for version 3.3: srcvdpower, phase, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2"""
        #now get statistics per path
        for rays in range(0,n_paths):
            line = self._get_next_line()
            line_values_as_list = line.split() #split line and organize values as list
            if len(line_values_as_list) == 8: #version 3.2
                ray_n, n_interactions, srcvdpower, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2 = [float(i) for i in line.split()]
            elif len(line_values_as_list) == 9: #version 3.3
                ray_n, n_interactions, srcvdpower, phase, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2  = [float(i) for i in line.split()]
            else:
                raise Exception(line + ' has ' + len(line_values_as_list) + ' but was expecting 8 or 9!')
            interactions_list = self._get_next_line().strip()
            ray_n = int(ray_n)
            n_interactions = int(n_interactions)
            self.data[receiver][ray_n] = collections.OrderedDict()
            self.data[receiver][ray_n]['srcvdpower'] = srcvdpower
            if len(line_values_as_list) == 9: #version 3.3
                self.data[receiver][ray_n]['phase'] = phase
            self.data[receiver][ray_n]['arrival_time'] = arrival_time
            self.data[receiver][ray_n]['arrival_angle1'] = arrival_angle1
            self.data[receiver][ray_n]['arrival_angle2'] = arrival_angle2
            self.data[receiver][ray_n]['departure_angle1'] = departure_angle1
            self.data[receiver][ray_n]['departure_angle2'] = departure_angle2
            self.data[receiver][ray_n]['interactions_list'] = interactions_list
            self.data[receiver][ray_n]['interactions'] = collections.OrderedDict()
            self.data[receiver][ray_n]['n_interactions'] = n_interactions #store integer
            """Get coordinates of interactions"""
            for i in range(n_interactions+2): #add 2 to take in account Tx and Rx
                line = self._get_next_line()
                sp_line = line.split()
                interaction = i 
                coordinates = np.array([float(j) for j in sp_line[0:]])
                #self.data[receiver][ray_n]['interactions'][interactions_list.split('-')[i]] = coordinates
                self.data[receiver][ray_n]['interactions'][str(interaction)] = coordinates

    def get_total_received_power(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        return self.data[antenna_number]['received_power']

    def get_mean_time_of_arrival(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        return self.data[antenna_number]['arrival_time']

    def get_spread_delay(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        return self.data[antenna_number]['spread_delay']

    def get_arrival_time_ndarray(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'],))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths+1]['arrival_time']
        return data_ndarray

    def get_interactions_list(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        data = []
        for paths in range(self.data[antenna_number]['paths_number']):
            data.append(self.data[antenna_number][paths+1]['interactions_list'])
        return data

    def get_interactions_positions(self, antenna_number, ray_number):
        if self.data[antenna_number] is None:
            return None
        if self.data[antenna_number][ray_number] is None:
            return None
        data = []
        #self.data[receiver][ray_n]['interactions'][interaction]
        #add 2 to take in account Tx and Rx
        for paths in range(2 + self.data[antenna_number][ray_number]['n_interactions']):
            data.append(self.data[antenna_number][ray_number]['interactions'][str(paths)])
        return data

    def get_interactions_positions_as_string(self, antenna_number, ray_number):
        data = self.get_interactions_positions(antenna_number, ray_number)
        outputString = ''
        for i in range(len(data)-1):
            outputString = outputString + str(data[i][0]) + ' ' + str(data[i][1]) + ' ' + str(data[i][2]) + ','
        i = len(data)-1
        outputString += str(data[i][0]) + ' ' + str(data[i][1]) + ' ' + str(data[i][2])
        return outputString

    def get_departure_angle_ndarray(self, antenna_number):
        """ return the daparture angles as a ndarray        
        The array is shaped (number_paths, departure_angle1, departure_angle2)
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 2))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['departure_angle1']
            data_ndarray[paths][1]= self.data[antenna_number][paths+1]['departure_angle2']
        return data_ndarray

    def get_arrival_angle_ndarray(self, antenna_number):
        """Return the arrival angles as a ndarray
        The array is shaped (number_paths, arrival_angle1, arrival_angle2)
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 2))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['arrival_angle1']
            data_ndarray[paths][1]= self.data[antenna_number][paths+1]['arrival_angle2']
        return data_ndarray

    def get_p_gain_ndarray(self, antenna_number):
        """Return the gains as a ndarray
        The array is shaped (number_paths, arrival_angle1, arrival_angle2)
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number']))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths+1]['srcvdpower']
        return data_ndarray

    def get_p_phase_ndarray(self, antenna_number):
        """Return the phases as a ndarray.
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number']))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths+1]['phase']
        return data_ndarray

    def is_los(self, antenna_number):
        '''Check if each ray  (not the whole channel) is LOS or not'''
        if self.data[antenna_number] is None:
            return None
        num_paths = self.data[antenna_number]['paths_number']
        data_ndarray = np.zeros((num_paths,))
        for path_i in range(num_paths):
            interaction = self.data[antenna_number][path_i+1]['interactions_list']
            if interaction == 'Tx-Rx':
                data_ndarray[path_i] = 1 #it is LOS
            else:
                data_ndarray[path_i] = 0 #it is not LOS
        return data_ndarray

    def is_los_through_foliage(self, antenna_number):
        '''Check if each ray  (not the whole channel) is LOS or not'''
        if self.data[antenna_number] is None:
            return None
        num_paths = self.data[antenna_number]['paths_number']
        data_ndarray = np.zeros((num_paths,))
        for path_i in range(num_paths):
            interaction = self.data[antenna_number][path_i+1]['interactions_list']
            if interaction == 'Tx-F-Rx' or interaction == 'Tx-F-X-Rx':
                data_ndarray[path_i] = 1 #it is LOS
            else:
                data_ndarray[path_i] = 0 #it is not LOS
        return data_ndarray

    def get_6_parameters_for_all_rays(self, antenna_number):
        """Useful for version 3.2, which does not inform the phase on .p2m files.
        Return all 6 parameters for all rays of a channel as ndarray
        The array is shaped (number_paths, 6)
        The order is:
                            thisRayInfo[0] = ray.path_gain
                            thisRayInfo[1] = ray.time_of_arrival
                            thisRayInfo[2] = ray.departure_elevation
                            thisRayInfo[3] = ray.departure_azimuth
                            thisRayInfo[4] = ray.arrival_elevation
                            thisRayInfo[5] = ray.arrival_azimuth

        Later we may add:
                            thisRayInfo[6] = ray.is_los
                            if numParametersPerRay == 8:
                                thisRayInfo[7] = ray.phaseInDegrees
        """
        if self.data[antenna_number] is None:
            return None
        num_paths = self.data[antenna_number]['paths_number']
        data_ndarray = np.zeros((num_paths,6))
        data_ndarray[:,0]=self.get_p_gain_ndarray(antenna_number)
        data_ndarray[:,1]=self.get_arrival_time_ndarray(antenna_number)
        data_ndarray[:,2:4] = self.get_departure_angle_ndarray(antenna_number)
        data_ndarray[:,4:6] = self.get_arrival_angle_ndarray(antenna_number)
        return data_ndarray

    def get_7_parameters_for_all_rays(self, antenna_number):
        """Version 3.3 informs the phase.
        Return all 7 parameters for all rays of a channel as ndarray
        The array is shaped (number_paths, 7)
        The order is:
                            thisRayInfo[0] = ray.path_gain
                            thisRayInfo[1] = ray.time_of_arrival
                            thisRayInfo[2] = ray.departure_elevation
                            thisRayInfo[3] = ray.departure_azimuth
                            thisRayInfo[4] = ray.arrival_elevation
                            thisRayInfo[5] = ray.arrival_azimuth
                            thisRayInfo[6] = ray.path_phase
        """
        if self.data[antenna_number] is None:
            return None
        num_paths = self.data[antenna_number]['paths_number']
        data_ndarray = np.zeros((num_paths,7))
        data_ndarray[:,0]=self.get_p_gain_ndarray(antenna_number)
        data_ndarray[:,1]=self.get_arrival_time_ndarray(antenna_number)
        data_ndarray[:,2:4] = self.get_departure_angle_ndarray(antenna_number)
        data_ndarray[:,4:6] = self.get_arrival_angle_ndarray(antenna_number)
        data_ndarray[:,6] = self.get_p_phase_ndarray(antenna_number)
        return data_ndarray

if __name__=='__main__':
    #InSite version 3.2 example:
    #path = P2mPaths('D:/insitedata/results_long_episodes/run00000/study/model.paths.t001_01.r002.p2m')
    #InSite version 3.3 example:
    path = P2mPaths('D:/insitedata/2019_04_19_fixed_ul_dl/ul_simu_3.3/run00008/study/model.paths.t001_02.r001.p2m')
    #path = P2mPaths('example/iter0.paths.t001_05.r006.p2m')
    print('Departure angles: ',path.get_departure_angle_ndarray(1)) #Pass the antenna_number as argument
    print('Arrival angles: ',path.get_arrival_angle_ndarray(1))
    print('Gains: ',path.get_p_gain_ndarray(1))
    print('Phases: ',path.get_p_phase_ndarray(1))
    print('Interactions: ',path.get_interactions_list(1))
    print('Interactions positions: ',path.get_interactions_positions(1, 3)) #receiver 2, ray 3
    print('Interactions positions as string: ',path.get_interactions_positions_as_string(1, 3)) #receiver 2, ray 3
